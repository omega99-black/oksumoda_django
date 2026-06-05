"""
apps/admin_panel/views.py — VERSION CORREGIDA
──────────────────────────────────────────────
Correcciones aplicadas:
  1. Filtros activo/inactivo ahora funcionan correctamente en todas las vistas.
  2. Vista 'categorias' ahora muestra categorías + subcategorías derivadas
     de los productos existentes (ya que Categoria solo guarda el nombre
     y la subcategoría vive en Producto).
  3. Nuevo endpoint /admin/api/ventas/ con datos diarios para gráficas.
  4. api_reportes devuelve también ventas_por_dia y top_productos completo
     con porcentaje calculado para las barras dinámicas.
  5. Dashboard summary muestra ventas reales del día.
  6. Mensaje de error cuando un admin intenta acceder al carrito.
  7. [FIX] _categorias_enriquecidas() centraliza el enriquecimiento de
     categorías para que guardar_categoria y eliminar_categoria devuelvan
     el contexto correcto al template en caso de error.
"""

import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db import IntegrityError, OperationalError
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal, InvalidOperation
from django.db.models import Sum, Count

from apps.usuarios.decorators import admin_requerido
from apps.usuarios.models import Usuario, Rol
from apps.productos.models import Producto
from apps.categorias.models import Categoria
from apps.clientes.models import Cliente


# ══════════════════════════════════════════════════════════════════════════════
# REGEX DE VALIDACIÓN
# ══════════════════════════════════════════════════════════════════════════════

NOMBRE_REGEX = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s\-']+$")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS DE REPORTES
# ══════════════════════════════════════════════════════════════════════════════

def _fmt_cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000"""
    return f"${valor:,.0f}".replace(',', '.')


def _ventas_ultimos_30_dias():
    """
    Devuelve lista de {fecha, cantidad, ingresos} para los últimos 30 días.
    Usado por las gráficas de Chart.js en el frontend.
    """
    from apps.carrito.models import Venta

    hoy = timezone.now().date()
    inicio = hoy - timedelta(days=29)

    ventas_qs = (
        Venta.objects
        .filter(fecha_venta__date__gte=inicio)
        .extra(select={'dia': "DATE(fecha_venta)"})
        .values('dia')
        .annotate(cantidad=Count('id_venta'), ingresos=Sum('total_venta'))
        .order_by('dia')
    )

    mapa = {str(v['dia']): v for v in ventas_qs}

    resultado = []
    for i in range(30):
        d = inicio + timedelta(days=i)
        clave = str(d)
        entrada = mapa.get(clave, {})
        resultado.append({
            'fecha':    clave,
            'cantidad': entrada.get('cantidad', 0),
            'ingresos': float(entrada.get('ingresos') or 0),
        })
    return resultado


def _ventas_por_mes_anio():
    """
    Devuelve lista de {mes, cantidad, ingresos} para los últimos 12 meses.
    """
    from apps.carrito.models import Venta
    from django.db.models.functions import TruncMonth

    hace_12 = timezone.now() - timedelta(days=365)
    qs = (
        Venta.objects
        .filter(fecha_venta__gte=hace_12)
        .annotate(mes=TruncMonth('fecha_venta'))
        .values('mes')
        .annotate(cantidad=Count('id_venta'), ingresos=Sum('total_venta'))
        .order_by('mes')
    )
    return [
        {
            'mes':      v['mes'].strftime('%b %Y'),
            'cantidad': v['cantidad'],
            'ingresos': float(v['ingresos'] or 0),
        }
        for v in qs
    ]


def _calcular_reportes():
    """
    Calcula todas las métricas de reportes.
    Reutilizable desde la vista principal y desde el endpoint JSON de polling.
    """
    from apps.carrito.models import Venta, DetalleVenta

    ahora      = timezone.now()
    hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    semana_ini = hoy_inicio - timedelta(days=ahora.weekday())
    mes_ini    = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    anio_ini   = ahora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    def ventas_periodo(desde):
        return Venta.objects.filter(fecha_venta__gte=desde)

    def total_dinero(qs):
        r = qs.aggregate(t=Sum('total_venta'))['t']
        return float(r) if r else 0.0

    ventas_hoy_qs    = ventas_periodo(hoy_inicio)
    ventas_semana_qs = ventas_periodo(semana_ini)
    ventas_mes_qs    = ventas_periodo(mes_ini)
    ventas_anio_qs   = ventas_periodo(anio_ini)

    top_raw = list(
        DetalleVenta.objects
        .filter(venta__fecha_venta__gte=mes_ini)
        .values('producto__nombre')
        .annotate(total_uds=Sum('cantidad'), total_ing=Sum('subtotal'))
        .order_by('-total_uds')[:10]
    )

    max_uds = top_raw[0]['total_uds'] if top_raw else 1
    top_productos = []
    for p in top_raw:
        top_productos.append({
            'producto__nombre': p['producto__nombre'],
            'total_uds':        p['total_uds'],
            'total_ing':        float(p['total_ing'] or 0),
            'popularidad_pct':  round((p['total_uds'] / max_uds) * 100),
        })

    ventas_30d = _ventas_ultimos_30_dias()
    ventas_12m = _ventas_por_mes_anio()

    metodos = list(
        Venta.objects.values('metodo_pago')
        .annotate(cantidad=Count('id_venta'))
        .order_by('-cantidad')
    )

    productos_stock_bajo = list(
        Producto.objects
        .filter(stock__lte=5, estado='activo')
        .values('nombre', 'stock')
        .order_by('stock')[:8]
    )

    return {
        'ventasHoy':       ventas_hoy_qs.count(),
        'ventasSemana':    ventas_semana_qs.count(),
        'ventasMes':       ventas_mes_qs.count(),
        'ventasAnio':      ventas_anio_qs.count(),

        'ingresosHoy':     _fmt_cop(total_dinero(ventas_hoy_qs)),
        'ingresosSemana':  _fmt_cop(total_dinero(ventas_semana_qs)),
        'ingresosMes':     _fmt_cop(total_dinero(ventas_mes_qs)),
        'ingresosAnio':    _fmt_cop(total_dinero(ventas_anio_qs)),

        'totalProductos':  Producto.objects.count(),
        'totalClientes':   Cliente.objects.count(),
        'totalVentas':     Venta.objects.count(),
        'ingresosTotales': _fmt_cop(total_dinero(Venta.objects.all())),

        'topProductos': top_productos,

        'ventas30d':            ventas_30d,
        'ventas12m':            ventas_12m,
        'metodosPago':          metodos,
        'productosStockBajo':   productos_stock_bajo,

        'ultimaActualizacion': timezone.now().strftime('%H:%M:%S'),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINT JSON — polling de reportes
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def api_reportes(request):
    try:
        return JsonResponse(_calcular_reportes())
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@admin_requerido
def api_ventas_detalle(request):
    """
    GET /admin/api/ventas-detalle/
    Devuelve ventas recientes con detalle para la tabla interactiva.
    """
    try:
        from apps.carrito.models import Venta
        ventas = list(
            Venta.objects
            .select_related('cliente')
            .order_by('-fecha_venta')[:50]
            .values(
                'id_venta', 'cliente__nombre', 'fecha_venta',
                'total_venta', 'estado', 'metodo_pago'
            )
        )
        for v in ventas:
            v['fecha_venta'] = v['fecha_venta'].strftime('%d/%m/%Y %H:%M')
            v['total_venta'] = float(v['total_venta'])
        return JsonResponse({'ventas': ventas})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def dashboard(request):
    view   = request.GET.get('view', 'summary')
    obj_id = request.GET.get('id')

    error_param = request.GET.get('error')
    context = {'currentView': view}
    if error_param == 'no_compras':
        context['error'] = 'Los administradores no pueden realizar compras. Usa una cuenta de cliente.'

    try:
        if view == 'summary':
            from apps.carrito.models import Venta
            ahora = timezone.now()
            hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
            ingresos_hoy = Venta.objects.filter(
                fecha_venta__gte=hoy_inicio
            ).aggregate(t=Sum('total_venta'))['t'] or 0

            context.update({
                'totalUsuarios':    Usuario.objects.count(),
                'productosActivos': Producto.objects.filter(estado='activo').count(),
                'ventasHoy':        _fmt_cop(float(ingresos_hoy)),
                'totalClientes':    Cliente.objects.count(),
                'ventasHoyCount':   Venta.objects.filter(fecha_venta__gte=hoy_inicio).count(),
            })

        elif view in ('productos', 'new_producto', 'edit_producto'):
            nombre     = request.GET.get('nombre', '').strip() or None
            estado     = request.GET.get('estado', '').strip() or None
            precio_min = _to_decimal(request.GET.get('precioMin'))
            precio_max = _to_decimal(request.GET.get('precioMax'))
            stock_min  = _to_int(request.GET.get('stockMin'))

            productos = Producto.filtrar(nombre, estado, precio_min, precio_max, stock_min)

            context.update({
                'productos':       productos,
                'filtroNombre':    nombre or '',
                'filtroEstado':    estado or '',
                'filtroPrecioMin': request.GET.get('precioMin', ''),
                'filtroPrecioMax': request.GET.get('precioMax', ''),
                'filtroStockMin':  request.GET.get('stockMin', ''),
            })

            if view == 'new_producto':
                context['producto'] = Producto()
            elif view == 'edit_producto' and obj_id:
                context['producto'] = get_object_or_404(Producto, pk=obj_id)

        elif view in ('usuarios', 'new_usuario', 'edit_usuario'):
            nombre     = request.GET.get('nombre', '').strip() or None
            email      = request.GET.get('email', '').strip() or None
            rol_nombre = request.GET.get('rolNombre', '').strip() or None
            estado     = request.GET.get('estado', '').strip() or None

            usuarios = _filtrar_usuarios(nombre, email, rol_nombre, estado)

            context.update({
                'usuarios':        usuarios,
                'roles':           Rol.objects.all(),
                'filtroNombre':    nombre or '',
                'filtroEmail':     email or '',
                'filtroRolNombre': rol_nombre or '',
                'filtroEstado':    estado or '',
            })

            if view == 'new_usuario':
                u = Usuario()
                u.estado = 'activo'
                context['usuario'] = u
            elif view == 'edit_usuario' and obj_id:
                context['usuario'] = get_object_or_404(Usuario, pk=obj_id)

        elif view in ('categorias', 'new_categoria', 'edit_categoria'):
            nombre = request.GET.get('nombre', '').strip() or None

            context.update({
                'categorias':   _categorias_enriquecidas(nombre),
                'filtroNombre': nombre or '',
            })

            if view == 'new_categoria':
                context['categoria'] = Categoria()
            elif view == 'edit_categoria' and obj_id:
                context['categoria'] = get_object_or_404(Categoria, pk=obj_id)

        elif view in ('clientes', 'new_cliente', 'edit_cliente'):
            nombre   = request.GET.get('nombre', '').strip() or None
            email    = request.GET.get('email', '').strip() or None
            telefono = request.GET.get('telefono', '').strip() or None
            estado   = request.GET.get('estado', '').strip() or None

            clientes = Cliente.filtrar(nombre, email, telefono, estado)

            context.update({
                'clientes':       clientes,
                'filtroNombre':   nombre or '',
                'filtroEmail':    email or '',
                'filtroTelefono': telefono or '',
                'filtroEstado':   estado or '',
            })

            if view == 'new_cliente':
                c = Cliente()
                c.estado = 'activo'
                context['cliente'] = c
            elif view == 'edit_cliente' and obj_id:
                context['cliente'] = get_object_or_404(Cliente, pk=obj_id)

        elif view == 'ventas':
            from apps.carrito.models import Venta
            estado_filtro = request.GET.get('estado', '').strip() or None
            metodo_filtro = request.GET.get('metodo', '').strip() or None

            ventas_qs = Venta.objects.select_related('cliente').order_by('-fecha_venta')
            if estado_filtro:
                ventas_qs = ventas_qs.filter(estado__iexact=estado_filtro)
            if metodo_filtro:
                ventas_qs = ventas_qs.filter(metodo_pago__iexact=metodo_filtro)

            total_ingresos = ventas_qs.aggregate(t=Sum('total_venta'))['t'] or 0
            ahora = timezone.now()
            hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

            context.update({
                'ventas':         ventas_qs[:100],
                'totalVentas':    ventas_qs.count(),
                'totalIngresos':  _fmt_cop(float(total_ingresos)),
                'filtroEstado':   estado_filtro or '',
                'filtroMetodo':   metodo_filtro or '',
            })

        elif view == 'reportes':
            context.update(_calcular_reportes())

    except OperationalError as e:
        context['error'] = f'Error de base de datos: {str(e)}'
    except Exception as e:
        context['error'] = f'Error inesperado: {str(e)}'

    return render(request, 'admin/dashboard.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCTOS
# ══════════════════════════════════════════════════════════════════════════════

@require_POST
@admin_requerido
def guardar_producto(request):
    prod_id = request.POST.get('id_producto') or None
    context = {'currentView': 'edit_producto' if prod_id else 'new_producto'}

    try:
        if prod_id:
            producto = get_object_or_404(Producto, pk=prod_id)
        else:
            producto = Producto()

        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            raise ValueError('El nombre del producto es obligatorio.')
        if len(nombre) < 2:
            raise ValueError('El nombre del producto debe tener al menos 2 caracteres.')
        if not NOMBRE_REGEX.match(nombre):
            raise ValueError(
                'El nombre del producto solo puede contener letras, espacios y guiones.'
            )

        precio = _to_decimal(request.POST.get('precio'))
        if precio is None:
            raise ValueError('El precio es obligatorio y debe ser un número válido.')
        if precio <= 0:
            raise ValueError('El precio debe ser mayor a 0.')

        stock = _to_int(request.POST.get('stock'))
        if stock is None:
            raise ValueError('El stock es obligatorio y debe ser un número entero.')
        if stock < 0:
            raise ValueError('El stock no puede ser negativo.')

        producto.nombre       = nombre
        producto.descripcion  = request.POST.get('descripcion', '')
        producto.estado       = request.POST.get('estado', 'activo')
        producto.precio       = precio
        producto.stock        = stock
        producto.categoria    = request.POST.get('categoria', '')
        producto.subcategoria = request.POST.get('subcategoria', '')
        producto.colores      = request.POST.get('colores', '')
        producto.tallas       = request.POST.get('tallas', '')
        producto.es_nuevo     = request.POST.get('es_nuevo') == 'on'

        precio_anterior = _to_decimal(request.POST.get('precio_anterior'))
        if precio_anterior is not None:
            if precio_anterior <= 0:
                raise ValueError('El precio anterior debe ser mayor a 0.')
            producto.precio_anterior = precio_anterior

        archivo = request.FILES.get('foto_archivo')
        if archivo:
            import cloudinary.uploader
            resultado = cloudinary.uploader.upload(
                archivo,
                folder='oksumoda/productos',
                overwrite=True,
                resource_type='image',
            )
            producto.foto = resultado['secure_url']
        else:
            foto_existente = request.POST.get('foto', '')
            if foto_existente:
                producto.foto = foto_existente
                
        producto.save()
        return redirect('/admin/dashboard/?view=productos')

        producto.save()
        return redirect('/admin/dashboard/?view=productos')

    except ValueError as e:
        context['error'] = str(e)
        context['producto'] = producto if prod_id else Producto()
        context['productos'] = Producto.filtrar()
        return render(request, 'admin/dashboard.html', context)

    except IntegrityError:
        context['error'] = 'Ya existe un producto con esos datos.'
        context['producto'] = producto if prod_id else Producto()
        context['productos'] = Producto.filtrar()
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        context['error'] = f'Error inesperado al guardar el producto: {str(e)}'
        context['producto'] = Producto()
        context['productos'] = Producto.filtrar()
        return render(request, 'admin/dashboard.html', context)


@admin_requerido
def eliminar_producto(request, pk):
    try:
        get_object_or_404(Producto, pk=pk).delete()
        return redirect('/admin/dashboard/?view=productos')
    except IntegrityError:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'productos',
            'productos': Producto.filtrar(),
            'error': 'No se puede eliminar el producto porque está relacionado con otros registros.'
        })
    except Exception as e:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'productos',
            'productos': Producto.filtrar(),
            'error': f'Error inesperado al eliminar el producto: {str(e)}'
        })


# ══════════════════════════════════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

@require_POST
@admin_requerido
def guardar_usuario(request):
    user_id = request.POST.get('id_usuario') or None
    context = {'currentView': 'edit_usuario' if user_id else 'new_usuario'}

    try:
        if user_id:
            usuario = get_object_or_404(Usuario, pk=user_id)
            nueva_contrasena = request.POST.get('contrasena', '').strip()
            if nueva_contrasena:
                if len(nueva_contrasena) < 6:
                    raise ValueError('La contraseña debe tener al menos 6 caracteres.')
                usuario.set_password(nueva_contrasena)
        else:
            usuario = Usuario()
            contrasena = request.POST.get('contrasena', '').strip()
            if not contrasena:
                raise ValueError('La contraseña es obligatoria para nuevos usuarios.')
            if len(contrasena) < 6:
                raise ValueError('La contraseña debe tener al menos 6 caracteres.')
            usuario.set_password(contrasena)

        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            raise ValueError('El nombre del usuario es obligatorio.')
        if len(nombre) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres.')
        if not NOMBRE_REGEX.match(nombre):
            raise ValueError('El nombre solo puede contener letras, espacios y guiones.')

        email = request.POST.get('email', '').strip()
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        if not _es_email_valido(email):
            raise ValueError('El correo electrónico no tiene un formato válido.')

        usuario.nombre = nombre
        usuario.email  = email
        usuario.estado = request.POST.get('estado', 'activo')

        rol_id = request.POST.get('rol_id') or request.POST.get('rol')
        if rol_id:
            usuario.rol = get_object_or_404(Rol, pk=rol_id)

        usuario.save()
        return redirect('/admin/dashboard/?view=usuarios')

    except ValueError as e:
        context['error'] = str(e)
        context['usuario'] = usuario if user_id else Usuario()
        context['usuarios'] = _filtrar_usuarios()
        context['roles'] = Rol.objects.all()
        return render(request, 'admin/dashboard.html', context)

    except IntegrityError:
        context['error'] = 'El correo electrónico ya está registrado.'
        context['usuario'] = Usuario()
        context['usuarios'] = _filtrar_usuarios()
        context['roles'] = Rol.objects.all()
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        context['error'] = f'Error inesperado al guardar el usuario: {str(e)}'
        context['usuario'] = Usuario()
        context['usuarios'] = _filtrar_usuarios()
        context['roles'] = Rol.objects.all()
        return render(request, 'admin/dashboard.html', context)


@admin_requerido
def eliminar_usuario(request, pk):
    try:
        get_object_or_404(Usuario, pk=pk).delete()
        return redirect('/admin/dashboard/?view=usuarios')
    except IntegrityError:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'usuarios',
            'usuarios': _filtrar_usuarios(),
            'roles': Rol.objects.all(),
            'error': 'No se puede eliminar el usuario porque está relacionado con otros registros.'
        })
    except Exception as e:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'usuarios',
            'usuarios': _filtrar_usuarios(),
            'roles': Rol.objects.all(),
            'error': f'Error inesperado al eliminar el usuario: {str(e)}'
        })


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORÍAS
# ══════════════════════════════════════════════════════════════════════════════

@require_POST
@admin_requerido
def guardar_categoria(request):
    cat_id = request.POST.get('id_categoria') or None
    context = {'currentView': 'edit_categoria' if cat_id else 'new_categoria'}

    try:
        if cat_id:
            categoria = get_object_or_404(Categoria, pk=cat_id)
        else:
            categoria = Categoria()

        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            raise ValueError('El nombre de la categoría es obligatorio.')
        if len(nombre) < 2:
            raise ValueError('El nombre de la categoría debe tener al menos 2 caracteres.')
        if not NOMBRE_REGEX.match(nombre):
            raise ValueError('El nombre de la categoría solo puede contener letras, espacios y guiones.')

        categoria.nombre = nombre
        categoria.save()
        return redirect('/admin/dashboard/?view=categorias')

    except ValueError as e:
        context['error'] = str(e)
        context['categoria'] = categoria if cat_id else Categoria()
        context['categorias'] = _categorias_enriquecidas()   # ← FIX
        return render(request, 'admin/dashboard.html', context)

    except IntegrityError:
        context['error'] = 'Ya existe una categoría con ese nombre.'
        context['categoria'] = Categoria()
        context['categorias'] = _categorias_enriquecidas()   # ← FIX
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        context['error'] = f'Error inesperado al guardar la categoría: {str(e)}'
        context['categoria'] = Categoria()
        context['categorias'] = _categorias_enriquecidas()   # ← FIX
        return render(request, 'admin/dashboard.html', context)


@admin_requerido
def eliminar_categoria(request, pk):
    try:
        get_object_or_404(Categoria, pk=pk).delete()
        return redirect('/admin/dashboard/?view=categorias')
    except IntegrityError:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'categorias',
            'categorias': _categorias_enriquecidas(),         # ← FIX
            'error': 'No se puede eliminar la categoría porque tiene productos asociados.'
        })
    except Exception as e:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'categorias',
            'categorias': _categorias_enriquecidas(),         # ← FIX
            'error': f'Error inesperado al eliminar la categoría: {str(e)}'
        })


# ══════════════════════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

@require_POST
@admin_requerido
def guardar_cliente(request):
    from django.contrib.auth.hashers import make_password

    cliente_id = request.POST.get('id_cliente') or None
    context = {'currentView': 'edit_cliente' if cliente_id else 'new_cliente'}

    try:
        if cliente_id:
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            nueva_contrasena = request.POST.get('contrasena', '').strip()
            if nueva_contrasena:
                if len(nueva_contrasena) < 6:
                    raise ValueError('La contraseña debe tener al menos 6 caracteres.')
                if not nueva_contrasena.startswith('$2a$') and not nueva_contrasena.startswith('pbkdf2_'):
                    cliente.contrasena = make_password(nueva_contrasena)
        else:
            cliente = Cliente()
            contrasena = request.POST.get('contrasena', '').strip()
            if contrasena and len(contrasena) < 6:
                raise ValueError('La contraseña debe tener al menos 6 caracteres.')
            cliente.contrasena = make_password(contrasena) if contrasena else make_password('cliente123')

        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            raise ValueError('El nombre del cliente es obligatorio.')
        if len(nombre) < 2:
            raise ValueError('El nombre del cliente debe tener al menos 2 caracteres.')
        if not NOMBRE_REGEX.match(nombre):
            raise ValueError('El nombre del cliente solo puede contener letras, espacios y guiones.')

        email = request.POST.get('email', '').strip()
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        if not _es_email_valido(email):
            raise ValueError('El correo electrónico no tiene un formato válido.')

        telefono = request.POST.get('telefono', '').strip()
        if telefono and not _es_telefono_valido(telefono):
            raise ValueError('El teléfono solo puede contener dígitos, espacios, guiones y +.')

        cliente.nombre   = nombre
        cliente.email    = email
        cliente.telefono = telefono
        cliente.estado   = request.POST.get('estado', 'activo')
        cliente.save()
        return redirect('/admin/dashboard/?view=clientes')

    except ValueError as e:
        context['error'] = str(e)
        context['cliente'] = cliente if cliente_id else Cliente()
        context['clientes'] = Cliente.filtrar()
        return render(request, 'admin/dashboard.html', context)

    except IntegrityError:
        context['error'] = 'El correo electrónico ya está registrado.'
        context['cliente'] = Cliente()
        context['clientes'] = Cliente.filtrar()
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        context['error'] = f'Error inesperado al guardar el cliente: {str(e)}'
        context['cliente'] = Cliente()
        context['clientes'] = Cliente.filtrar()
        return render(request, 'admin/dashboard.html', context)


@admin_requerido
def eliminar_cliente(request, pk):
    try:
        get_object_or_404(Cliente, pk=pk).delete()
        return redirect('/admin/dashboard/?view=clientes')
    except IntegrityError:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'clientes',
            'clientes': Cliente.filtrar(),
            'error': 'No se puede eliminar el cliente porque tiene registros asociados.'
        })
    except Exception as e:
        return render(request, 'admin/dashboard.html', {
            'currentView': 'clientes',
            'clientes': Cliente.filtrar(),
            'error': f'Error inesperado al eliminar el cliente: {str(e)}'
        })


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS PRIVADOS
# ══════════════════════════════════════════════════════════════════════════════

def _to_decimal(value):
    if value is None:
        return None
    try:
        v = str(value).strip()
        return Decimal(v) if v else None
    except InvalidOperation:
        return None


def _to_int(value):
    if value is None:
        return None
    try:
        v = str(value).strip()
        return int(v) if v else None
    except ValueError:
        return None


def _es_email_valido(email: str) -> bool:
    patron = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(patron.match(email))


def _es_telefono_valido(telefono: str) -> bool:
    patron = re.compile(r'^\+?[\d\s\-]{6,20}$')
    return bool(patron.match(telefono))


def _filtrar_usuarios(nombre=None, email=None, rol_nombre=None, estado=None):
    qs = Usuario.objects.select_related('rol').all()
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)
    if email:
        qs = qs.filter(email__icontains=email)
    if rol_nombre:
        qs = qs.filter(rol__nombre__iexact=rol_nombre)
    if estado:
        qs = qs.filter(estado__iexact=estado)
    return qs


def _categorias_enriquecidas(nombre=None):
    """
    [FIX] Devuelve lista de dicts con id_categoria, nombre, subcategorias
    y total_productos listos para el template.

    Se usa tanto en dashboard() como en guardar_categoria() y
    eliminar_categoria() para garantizar que el template siempre reciba
    los datos en el formato correcto, incluso cuando ocurre un error.

    El problema original: guardar_categoria/eliminar_categoria pasaban
    Categoria.filtrar() crudo (objetos Django sin los atributos
    'subcategorias' ni 'total_productos'), causando que el template
    renderizara la tabla vacía.
    """
    categorias_bd = Categoria.filtrar(nombre)
    resultado = []
    for cat in categorias_bd:
        subs = list(
            Producto.objects
            .filter(categoria__iexact=cat.nombre)
            .exclude(subcategoria__isnull=True)
            .exclude(subcategoria='')
            .values_list('subcategoria', flat=True)
            .distinct()
            .order_by('subcategoria')
        )
        total = Producto.objects.filter(categoria__iexact=cat.nombre).count()
        resultado.append({
            'id_categoria':    cat.id_categoria,
            'nombre':          cat.nombre,
            'subcategorias':   subs,
            'total_productos': total,
        })
    return resultado