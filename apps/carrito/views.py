"""
apps/carrito/views.py
"""

from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from apps.usuarios.decorators import cliente_o_admin_requerido
from . import services


@cliente_o_admin_requerido
def ver_carrito(request):
    return render(request, 'carrito.html', {
        'items':           services.obtener_items(request.session),
        'total':           services.calcular_total(request.session),
        'cantidadItems':   services.obtener_cantidad_items(request.session),
        'pagina_anterior': request.session.get('pagina_anterior', '/'),
    })


@require_POST
@login_required(login_url='/login/')
def agregar(request):
    try:
        producto_id = int(request.POST.get('productoId', 0))
        cantidad    = int(request.POST.get('cantidad', 1))
        talla       = request.POST.get('talla', '')
        color       = request.POST.get('color', '')

        services.agregar_producto(request.session, producto_id, cantidad, talla, color)

        return JsonResponse({
            'success':       True,
            'message':       'Producto agregado al carrito',
            'cantidadItems': services.obtener_cantidad_items(request.session),
        })

    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
@login_required(login_url='/login/')
def eliminar(request, producto_id):
    try:
        services.eliminar_producto(request.session, producto_id)
        return JsonResponse({
            'success':       True,
            'message':       'Producto eliminado del carrito',
            'cantidadItems': services.obtener_cantidad_items(request.session),
            'total':         str(services.calcular_total(request.session)),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error al eliminar el producto'})


@require_POST
@login_required(login_url='/login/')
def actualizar(request, producto_id):
    try:
        cantidad = int(request.POST.get('cantidad', 1))
        services.actualizar_cantidad(request.session, producto_id, cantidad)
        return JsonResponse({
            'success':       True,
            'cantidadItems': services.obtener_cantidad_items(request.session),
            'total':         str(services.calcular_total(request.session)),
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})


def cantidad(request):
    if request.user.is_authenticated:
        cant = services.obtener_cantidad_items(request.session)
    else:
        cant = 0
    return JsonResponse({'cantidadItems': cant})


@require_POST
@login_required(login_url='/login/')
def vaciar(request):
    try:
        services.vaciar_carrito(request.session)
    except Exception:
        pass
    return redirect('/carrito/')


@cliente_o_admin_requerido
def checkout(request):
    if services.esta_vacio(request.session):
        return redirect('/carrito/')

    subtotal = services.calcular_total(request.session)
    envio    = Decimal('0') if subtotal >= Decimal('150000') else Decimal('10000')
    total    = subtotal + envio

    if request.method == 'POST':
        from apps.carrito.models import Venta, DetalleVenta
        from apps.clientes.models import Cliente
        from apps.productos.models import Producto

        metodo_pago = request.POST.get('metodo_pago', 'efectivo')

        try:
            cliente = Cliente.objects.get(email=request.user.email)
            items   = services.obtener_items(request.session)

            venta = Venta.objects.create(
                cliente=cliente,
                total_venta=total,
                estado='completada',
                metodo_pago=metodo_pago,
            )

            for item in items:
                producto      = Producto.objects.get(pk=item['producto_id'])
                cantidad_item = item['cantidad']
                precio_unit   = Decimal(str(item['precio']))
                subtotal_item = precio_unit * cantidad_item

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad_item,
                    precio_unit=precio_unit,
                    subtotal=subtotal_item,
                )

            print(f'✅ Venta #{venta.id_venta} registrada correctamente')

        except Cliente.DoesNotExist:
            print(f'⚠️ No se encontró cliente con email: {request.user.email}')
        except Exception as e:
            print(f'❌ Error al registrar venta: {e}')

        services.vaciar_carrito(request.session)
        return render(request, 'confirmacion_pago.html', {
            'metodo_pago':   metodo_pago,
            'total':         total,
            'cantidadItems': 0,
        })

    return render(request, 'checkout.html', {
        'items':         services.obtener_items(request.session),
        'subtotal':      subtotal,
        'envio':         envio,
        'total':         total,
        'cantidadItems': services.obtener_cantidad_items(request.session),
    })