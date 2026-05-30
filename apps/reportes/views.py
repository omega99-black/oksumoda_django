"""
apps/reportes/views.py

Equivalente a:
  - Utils/PdfGenerator.java       (genera PDF desde plantilla)
  - AdminController.reporteUsuarios()
  - AdminController.reporteProductos()
  - AdminController.reporteCategorias()
  - AdminController.reporteClientes()

En Java se usaba Flying Saucer (ITextRenderer) + FreeMarker.
En Python usamos ReportLab para generar el PDF directamente
(sin plantilla HTML intermedia, más simple y robusto).
"""

from io import BytesIO
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from apps.usuarios.decorators import admin_requerido
from apps.usuarios.models import Usuario
from apps.productos.models import Producto
from apps.categorias.models import Categoria
from apps.clientes.models import Cliente


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Equivalente a PdfGenerator.generarPdf()
# ══════════════════════════════════════════════════════════════════════════════

def _crear_response_pdf(nombre_archivo: str) -> tuple:
    """
    Equivalente a:
      response.setContentType("application/pdf");
      response.setHeader("Content-Disposition", "attachment; filename=...");
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
    buffer = BytesIO()
    return response, buffer


def _estilos_base():
    """Estilos reutilizables — equivalente al CSS en las plantillas .ftl"""
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    return styles, titulo_style, subtitulo_style


def _tabla_estilo_base(num_cols: int):
    """
    Estilo de tabla equivalente al <table> con estilos en las plantillas FreeMarker.
    """
    return TableStyle([
        # Cabecera
        ('BACKGROUND',  (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0), 9),
        ('ALIGN',       (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING',  (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

        # Filas de datos
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 1), (-1, -1), 8),
        ('ALIGN',       (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',  (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),

        # Filas alternas (zebra)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f8f9fa')]),

        # Bordes
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('BOX',         (0, 0), (-1, -1), 1,   colors.HexColor('#2c3e50')),
    ])


def _build_pdf(buffer, titulo: str, elementos: list):
    """
    Construye el PDF. Equivalente a:
      renderer.setDocumentFromString(html)
      renderer.layout()
      renderer.createPDF(out)
    """
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=1.5 * cm,
    )

    _, titulo_style, subtitulo_style = _estilos_base()

    contenido = [
        Paragraph('Oksumoda', titulo_style),
        Paragraph(titulo, ParagraphStyle(
            'TituloReporte',
            fontSize=13,
            textColor=colors.HexColor('#555'),
            alignment=TA_CENTER,
            spaceAfter=4,
        )),
        Paragraph(
            f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}',
            subtitulo_style,
        ),
        HRFlowable(width='100%', thickness=1, color=colors.HexColor('#2c3e50')),
        Spacer(1, 0.4 * cm),
    ]
    contenido.extend(elementos)
    doc.build(contenido)


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE USUARIOS
# Equivalente a AdminController.reporteUsuarios()
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_usuarios(request):
    """
    GET /admin/reportes/usuarios/?nombre=&email=&rolNombre=&estado=
    Equivalente a AdminController.reporteUsuarios()
    """
    nombre     = request.GET.get('nombre')
    email      = request.GET.get('email')
    rol_nombre = request.GET.get('rolNombre')
    estado     = request.GET.get('estado')

    print(f'🎯 reporte_usuarios() — filtros: nombre={nombre}, email={email}, '
          f'rolNombre={rol_nombre}, estado={estado}')

    qs = Usuario.objects.select_related('rol').all()
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)
    if email:
        qs = qs.filter(email__icontains=email)
    if rol_nombre:
        qs = qs.filter(rol__nombre__iexact=rol_nombre)
    if estado:
        qs = qs.filter(estado__iexact=estado)

    response, buffer = _crear_response_pdf('reporte-usuarios')

    # Cabecera de tabla
    data = [['ID', 'Nombre', 'Email', 'Rol', 'Estado']]
    for u in qs:
        data.append([
            str(u.id_usuario),
            u.nombre,
            u.email,
            u.rol.nombre if u.rol else '—',
            u.estado,
        ])

    anchos = [1.5 * cm, 5 * cm, 6 * cm, 3.5 * cm, 2.5 * cm]
    tabla = Table(data, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_tabla_estilo_base(5))

    resumen = Paragraph(
        f'Total de usuarios encontrados: <b>{len(data) - 1}</b>',
        ParagraphStyle('Resumen', fontSize=9, textColor=colors.grey,
                       spaceBefore=8, alignment=TA_LEFT),
    )

    _build_pdf(buffer, 'Reporte de Usuarios', [tabla, Spacer(1, 0.3 * cm), resumen])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE PRODUCTOS
# Equivalente a AdminController.reporteProductos()
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_productos(request):
    """
    GET /admin/reportes/productos/?nombre=&estado=&precioMin=&precioMax=&stockMin=
    """
    from apps.admin_panel.views import _to_decimal, _to_int

    nombre     = request.GET.get('nombre')
    estado     = request.GET.get('estado')
    precio_min = _to_decimal(request.GET.get('precioMin'))
    precio_max = _to_decimal(request.GET.get('precioMax'))
    stock_min  = _to_int(request.GET.get('stockMin'))

    print(f'🎯 reporte_productos() — filtros: nombre={nombre}, estado={estado}, '
          f'precioMin={precio_min}, precioMax={precio_max}, stockMin={stock_min}')

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

    anchos = [1.2 * cm, 5.5 * cm, 3 * cm, 2.8 * cm, 1.8 * cm, 2.2 * cm]
    tabla = Table(data, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_tabla_estilo_base(6))

    resumen = Paragraph(
        f'Total de productos encontrados: <b>{len(data) - 1}</b>',
        ParagraphStyle('Resumen', fontSize=9, textColor=colors.grey,
                       spaceBefore=8, alignment=TA_LEFT),
    )

    _build_pdf(buffer, 'Reporte de Productos', [tabla, Spacer(1, 0.3 * cm), resumen])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE CATEGORÍAS
# Equivalente a AdminController.reporteCategorias()
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_categorias(request):
    """GET /admin/reportes/categorias/?nombre="""
    nombre = request.GET.get('nombre')

    print(f'🎯 reporte_categorias() — filtro: nombre={nombre}')

    categorias = Categoria.filtrar(nombre)

    response, buffer = _crear_response_pdf('reporte-categorias')

    data = [['ID', 'Nombre']]
    for c in categorias:
        data.append([str(c.id_categoria), c.nombre])

    anchos = [3 * cm, 14 * cm]
    tabla = Table(data, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_tabla_estilo_base(2))

    resumen = Paragraph(
        f'Total de categorías encontradas: <b>{len(data) - 1}</b>',
        ParagraphStyle('Resumen', fontSize=9, textColor=colors.grey,
                       spaceBefore=8, alignment=TA_LEFT),
    )

    _build_pdf(buffer, 'Reporte de Categorías', [tabla, Spacer(1, 0.3 * cm), resumen])

    response.write(buffer.getvalue())
    return response


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE CLIENTES
# Equivalente a AdminController.reporteClientes()
# ══════════════════════════════════════════════════════════════════════════════

@admin_requerido
def reporte_clientes(request):
    """GET /admin/reportes/clientes/?nombre=&email=&telefono=&estado="""
    nombre   = request.GET.get('nombre')
    email    = request.GET.get('email')
    telefono = request.GET.get('telefono')
    estado   = request.GET.get('estado')

    print(f'🎯 reporte_clientes() — filtros: nombre={nombre}, email={email}, '
          f'telefono={telefono}, estado={estado}')

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

    anchos = [1.5 * cm, 5 * cm, 5.5 * cm, 3 * cm, 2.5 * cm]
    tabla = Table(data, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_tabla_estilo_base(5))

    resumen = Paragraph(
        f'Total de clientes encontrados: <b>{len(data) - 1}</b>',
        ParagraphStyle('Resumen', fontSize=9, textColor=colors.grey,
                       spaceBefore=8, alignment=TA_LEFT),
    )

    _build_pdf(buffer, 'Reporte de Clientes', [tabla, Spacer(1, 0.3 * cm), resumen])

    response.write(buffer.getvalue())
    return response
