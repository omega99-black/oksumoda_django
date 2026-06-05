"""
apps/reportes/views.py
Estética Oksumoda: negro #0f0f0f, rojo #EB0029, minimalista.
"""

from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from apps.usuarios.decorators import admin_requerido
from apps.usuarios.models import Usuario
from apps.productos.models import Producto
from apps.categorias.models import Categoria
from apps.clientes.models import Cliente

# ── Colores de marca ──────────────────────────────────────────────────────────
ROJO   = colors.HexColor('#EB0029')
NEGRO  = colors.HexColor('#0f0f0f')
GRIS   = colors.HexColor('#767676')
GRIS_CL = colors.HexColor('#f4f4f2')
BLANCO = colors.white


def _crear_response_pdf(nombre_archivo: str):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
    buffer = BytesIO()
    return response, buffer


def _style(name, **kwargs):
    base = dict(fontName='Helvetica', fontSize=10, textColor=NEGRO)
    base.update(kwargs)
    return ParagraphStyle(name, **base)


def _build_pdf(buffer, titulo_reporte: str, elementos: list):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=1.5 * cm,
    )

    contenido = []

    # ── Cabecera: OKSUMODA en rojo ────────────────────────────────────────────
    contenido.append(Paragraph(
        'OKSUMODA',
        _style('marca',
               fontName='Helvetica-Bold',
               fontSize=22,
               textColor=ROJO,
               alignment=TA_CENTER,
               spaceAfter=2),
    ))

    # ── Subtítulo del reporte ─────────────────────────────────────────────────
    contenido.append(Paragraph(
        titulo_reporte,
        _style('titulo_rep',
               fontSize=11,
               textColor=GRIS,
               alignment=TA_CENTER,
               spaceAfter=3),
    ))

    # ── Fecha ─────────────────────────────────────────────────────────────────
    contenido.append(Paragraph(
        f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        _style('fecha',
               fontSize=8,
               textColor=GRIS,
               alignment=TA_CENTER,
               spaceAfter=10),
    ))

    # ── Línea roja ────────────────────────────────────────────────────────────
    contenido.append(HRFlowable(
        width='100%', thickness=2,
        color=ROJO, spaceAfter=14,
    ))

    contenido.extend(elementos)
    doc.build(contenido)


def _tabla_estilo(num_cols: int):
    return TableStyle([
        # Cabecera — negro sólido
        ('BACKGROUND',    (0, 0), (-1, 0), NEGRO),
        ('TEXTCOLOR',     (0, 0), (-1, 0), BLANCO),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 8),
        ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING',    (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 9),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),

        # Filas de datos
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8),
        ('TEXTCOLOR',     (0, 1), (-1, -1), NEGRO),
        ('ALIGN',         (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

        # Filas alternas — blanco y gris muy claro
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BLANCO, GRIS_CL]),

        # Sin bordes en filas — solo línea inferior fina
        ('LINEBELOW',     (0, 0), (-1, -1), 0.4, colors.HexColor('#e0e0e0')),

        # Línea roja debajo de la cabecera
        ('LINEBELOW',     (0, 0), (-1, 0), 1.5, ROJO),

        # Borde exterior negro fino
        ('BOX',           (0, 0), (-1, -1), 0.8, NEGRO),
    ])


def _resumen(texto: str):
    return Paragraph(
        texto,
        _style('resumen',
               fontSize=8,
               textColor=GRIS,
               spaceBefore=10,
               alignment=TA_LEFT),
    )


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_usuarios(request):
    nombre     = request.GET.get('nombre')
    email      = request.GET.get('email')
    rol_nombre = request.GET.get('rolNombre')
    estado     = request.GET.get('estado')

    qs = Usuario.objects.select_related('rol').all()
    if nombre:     qs = qs.filter(nombre__icontains=nombre)
    if email:      qs = qs.filter(email__icontains=email)
    if rol_nombre: qs = qs.filter(rol__nombre__iexact=rol_nombre)
    if estado:     qs = qs.filter(estado__iexact=estado)

    response, buffer = _crear_response_pdf('reporte-usuarios')

    data = [['ID', 'Nombre', 'Email', 'Rol', 'Estado']]
    for u in qs:
        data.append([
            str(u.id_usuario),
            u.nombre,
            u.email,
            u.rol.nombre if u.rol else '—',
            u.estado,
        ])

    tabla = Table(data,
                  colWidths=[1.5*cm, 4.5*cm, 6*cm, 3*cm, 2.5*cm],
                  repeatRows=1)
    tabla.setStyle(_tabla_estilo(5))

    _build_pdf(buffer, 'Reporte de Usuarios', [
        tabla,
        Spacer(1, 0.2*cm),
        _resumen(f'Total de usuarios encontrados: <b>{len(data)-1}</b>'),
    ])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE PRODUCTOS
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_productos(request):
    from apps.admin_panel.views import _to_decimal, _to_int

    nombre     = request.GET.get('nombre')
    estado     = request.GET.get('estado')
    precio_min = _to_decimal(request.GET.get('precioMin'))
    precio_max = _to_decimal(request.GET.get('precioMax'))
    stock_min  = _to_int(request.GET.get('stockMin'))

    productos = Producto.filtrar(nombre, estado, precio_min, precio_max, stock_min)

    response, buffer = _crear_response_pdf('reporte-productos')

    data = [['ID', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Estado']]
    for p in productos:
        data.append([
            str(p.id_producto),
            p.nombre,
            p.categoria or '—',
            f'${p.precio:,.0f}',
            str(p.stock),
            p.estado,
        ])

    tabla = Table(data,
                  colWidths=[1.2*cm, 5.5*cm, 3*cm, 2.8*cm, 1.8*cm, 2.2*cm],
                  repeatRows=1)
    tabla.setStyle(_tabla_estilo(6))

    # Resaltar en rojo las filas con stock 0
    for i, p in enumerate(productos, start=1):
        if p.stock == 0:
            tabla.setStyle(TableStyle([
                ('TEXTCOLOR', (4, i), (4, i), ROJO),
                ('FONTNAME',  (4, i), (4, i), 'Helvetica-Bold'),
            ]))

    _build_pdf(buffer, 'Reporte de Productos', [
        tabla,
        Spacer(1, 0.2*cm),
        _resumen(f'Total de productos encontrados: <b>{len(data)-1}</b>'),
    ])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE CATEGORÍAS
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_categorias(request):
    nombre = request.GET.get('nombre')
    categorias = Categoria.filtrar(nombre)

    response, buffer = _crear_response_pdf('reporte-categorias')

    data = [['ID', 'Nombre']]
    for c in categorias:
        data.append([str(c.id_categoria), c.nombre])

    tabla = Table(data, colWidths=[3*cm, 14*cm], repeatRows=1)
    tabla.setStyle(_tabla_estilo(2))

    _build_pdf(buffer, 'Reporte de Categorías', [
        tabla,
        Spacer(1, 0.2*cm),
        _resumen(f'Total de categorías encontradas: <b>{len(data)-1}</b>'),
    ])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_clientes(request):
    nombre   = request.GET.get('nombre')
    email    = request.GET.get('email')
    telefono = request.GET.get('telefono')
    estado   = request.GET.get('estado')

    clientes = Cliente.filtrar(nombre, email, telefono, estado)

    response, buffer = _crear_response_pdf('reporte-clientes')

    data = [['ID', 'Nombre', 'Email', 'Teléfono', 'Estado']]
    for c in clientes:
        data.append([
            str(c.id_cliente),
            c.nombre,
            c.email,
            c.telefono or '—',
            c.estado,
        ])

    tabla = Table(data,
                  colWidths=[1.5*cm, 5*cm, 5.5*cm, 3*cm, 2.5*cm],
                  repeatRows=1)
    tabla.setStyle(_tabla_estilo(5))

    _build_pdf(buffer, 'Reporte de Clientes', [
        tabla,
        Spacer(1, 0.2*cm),
        _resumen(f'Total de clientes encontrados: <b>{len(data)-1}</b>'),
    ])

    response.write(buffer.getvalue())
    return response