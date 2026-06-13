from unittest.mock import patch, MagicMock
from apps.productos.models import Producto


# ── get_colores_list() ──────────────────────────────────────────
def test_get_colores_list_con_valores():
    p = Producto()
    p.colores = "Negro,Blanco,Azul"
    assert p.get_colores_list() == ["Negro", "Blanco", "Azul"]


def test_get_colores_list_vacio():
    p = Producto()
    p.colores = None
    assert p.get_colores_list() == []


# ── get_tallas_list() ───────────────────────────────────────────
def test_get_tallas_list_con_valores():
    p = Producto()
    p.tallas = "S,M,L,XL"
    assert p.get_tallas_list() == ["S", "M", "L", "XL"]


def test_get_tallas_list_vacio():
    p = Producto()
    p.tallas = None
    assert p.get_tallas_list() == []


# ── filtrar() con mocks ─────────────────────────────────────────
@patch("apps.productos.models.Producto.objects")
def test_filtrar_por_nombre(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    mock_qs.filter.return_value = mock_qs

    Producto.filtrar(nombre="camisa")

    mock_qs.filter.assert_called_with(nombre__icontains="camisa")


@patch("apps.productos.models.Producto.objects")
def test_filtrar_sin_parametros(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs

    resultado = Producto.filtrar()

    mock_objects.all.assert_called_once()
    assert resultado == mock_qs


@patch("apps.productos.models.Producto.objects")
def test_filtrar_por_estado(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    mock_qs.filter.return_value = mock_qs

    Producto.filtrar(estado="activo")

    mock_qs.filter.assert_called_with(estado__iexact="activo")
    
    # ── Categoria.filtrar() ─────────────────────────────────────────
from apps.categorias.models import Categoria

@patch("apps.categorias.models.Categoria.objects")
def test_categoria_filtrar_sin_parametros(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    Categoria.filtrar()
    mock_objects.all.assert_called_once()

@patch("apps.categorias.models.Categoria.objects")
def test_categoria_filtrar_por_nombre(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    mock_qs.filter.return_value = mock_qs
    Categoria.filtrar(nombre="ropa")
    mock_qs.filter.assert_called_with(nombre__icontains="ropa")


# ── Cliente.filtrar() ───────────────────────────────────────────
from apps.clientes.models import Cliente

@patch("apps.clientes.models.Cliente.objects")
def test_cliente_filtrar_sin_parametros(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    Cliente.filtrar()
    mock_objects.all.assert_called_once()

@patch("apps.clientes.models.Cliente.objects")
def test_cliente_filtrar_por_email(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    mock_qs.filter.return_value = mock_qs
    Cliente.filtrar(email="test@mail.com")
    mock_qs.filter.assert_called_with(email__icontains="test@mail.com")

@patch("apps.clientes.models.Cliente.objects")
def test_cliente_filtrar_por_estado(mock_objects):
    mock_qs = MagicMock()
    mock_objects.all.return_value = mock_qs
    mock_qs.filter.return_value = mock_qs
    Cliente.filtrar(estado="activo")
    mock_qs.filter.assert_called_with(estado__iexact="activo")