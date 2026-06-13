import pytest
from django.test import Client
from apps.productos.models import Producto


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def producto_activo(db):
    return Producto.objects.create(
        nombre="Camiseta Test",
        precio=50000,
        stock=10,
        categoria="Hombres",
        estado="activo",
        colores="Negro,Blanco",
        tallas="S,M,L",
    )


# ── Rutas públicas ──────────────────────────────────────────────
def test_inicio(client):
    response = client.get('/')
    assert response.status_code == 200


def test_hombres(client, db):
    response = client.get('/hombres/')
    assert response.status_code == 200


def test_mujeres(client, db):
    response = client.get('/mujeres/')
    assert response.status_code == 200


def test_ninos(client, db):
    response = client.get('/ninos/')
    assert response.status_code == 200


def test_otros(client, db):
    response = client.get('/otros/')
    assert response.status_code == 200


def test_contactanos(client):
    response = client.get('/contactanos/')
    assert response.status_code == 200


# ── Búsqueda ────────────────────────────────────────────────────
def test_buscar_con_query(client, db):
    response = client.get('/buscar/?q=camisa')
    assert response.status_code == 200


def test_buscar_sin_query(client, db):
    response = client.get('/buscar/')
    assert response.status_code == 200


# ── Detalle de producto ─────────────────────────────────────────
def test_detalle_producto_existente(client, producto_activo):
    response = client.get(f'/producto/{producto_activo.pk}/')
    assert response.status_code == 200


def test_detalle_producto_inexistente(client, db):
    response = client.get('/producto/99999/')
    assert response.status_code == 404