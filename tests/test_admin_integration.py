import pytest
from django.test import Client
from apps.productos.models import Producto
from apps.categorias.models import Categoria
from apps.clientes.models import Cliente
from apps.usuarios.models import Usuario, Rol


# ── Fixtures ────────────────────────────────────────────────────

@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    rol, _ = Rol.objects.get_or_create(nombre='ADMIN')
    user = Usuario(
        email='admin@test.com',
        nombre='Admin Test',
        estado='activo',
        rol=rol,
    )
    user.set_password('admin123')
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    loggedin = client.login(email='admin@test.com', password='admin123')
    assert loggedin, "El login falló — revisa credenciales del fixture"
    return client


@pytest.fixture
def producto(db):
    return Producto.objects.create(
        nombre='Producto Test',
        precio=80000,
        stock=5,
        categoria='Hombres',
        estado='activo',
    )


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre='Hombres')


@pytest.fixture
def cliente_obj(db):
    return Cliente.objects.create(
        nombre='Cliente Test',
        email='cliente@test.com',
        contrasena='pbkdf2_sha256$test',
        estado='activo',
    )


# ── Dashboard ───────────────────────────────────────────────────

def test_dashboard_sin_login_redirige(client, db):
    response = client.get('/admin/dashboard/')
    assert response.status_code == 302


def test_dashboard_con_admin(admin_client, db):
    response = admin_client.get('/admin/dashboard/')
    assert response.status_code == 200


def test_dashboard_view_productos(admin_client, db):
    response = admin_client.get('/admin/dashboard/?view=productos')
    assert response.status_code == 200


def test_dashboard_view_usuarios(admin_client, db):
    response = admin_client.get('/admin/dashboard/?view=usuarios')
    assert response.status_code == 200


def test_dashboard_view_categorias(admin_client, db):
    response = admin_client.get('/admin/dashboard/?view=categorias')
    assert response.status_code == 200


def test_dashboard_view_clientes(admin_client, db):
    response = admin_client.get('/admin/dashboard/?view=clientes')
    assert response.status_code == 200


# ── Productos CRUD ──────────────────────────────────────────────

def test_crear_producto(admin_client, db):
    response = admin_client.post('/admin/productos/guardar/', {
        'nombre': 'Camisa Nueva',
        'precio': '75000',
        'stock': '10',
        'categoria': 'Hombres',
        'estado': 'activo',
    })
    assert response.status_code == 302
    assert Producto.objects.filter(nombre='Camisa Nueva').exists()


def test_crear_producto_sin_nombre(admin_client, db):
    response = admin_client.post('/admin/productos/guardar/', {
        'precio': '75000',
        'stock': '10',
    })
    assert response.status_code == 200


def test_editar_producto(admin_client, producto):
    response = admin_client.post('/admin/productos/guardar/', {
        'id_producto': producto.pk,
        'nombre': 'Producto Editado',
        'precio': '90000',
        'stock': '8',
        'estado': 'activo',
    })
    assert response.status_code == 302
    producto.refresh_from_db()
    assert producto.nombre == 'Producto Editado'


def test_eliminar_producto(admin_client, producto):
    pk = producto.pk
    response = admin_client.get(f'/admin/productos/eliminar/{pk}/')
    assert response.status_code == 302
    assert not Producto.objects.filter(pk=pk).exists()


def test_eliminar_producto_inexistente(admin_client, db):
    response = admin_client.get('/admin/productos/eliminar/99999/')
    assert response.status_code == 404


# ── Categorías CRUD ─────────────────────────────────────────────

def test_crear_categoria(admin_client, db):
    response = admin_client.post('/admin/categorias/guardar/', {
        'nombre': 'Accesorios',
    })
    assert response.status_code == 302
    assert Categoria.objects.filter(nombre='Accesorios').exists()


def test_crear_categoria_sin_nombre(admin_client, db):
    response = admin_client.post('/admin/categorias/guardar/', {})
    assert response.status_code == 200


def test_eliminar_categoria(admin_client, categoria):
    pk = categoria.pk
    response = admin_client.get(f'/admin/categorias/eliminar/{pk}/')
    assert response.status_code == 302
    assert not Categoria.objects.filter(pk=pk).exists()


def test_eliminar_categoria_inexistente(admin_client, db):
    response = admin_client.get('/admin/categorias/eliminar/99999/')
    assert response.status_code == 404


# ── Clientes CRUD ───────────────────────────────────────────────

def test_crear_cliente(admin_client, db):
    response = admin_client.post('/admin/clientes/guardar/', {
        'nombre': 'Juan Perez',
        'email': 'juan@test.com',
        'telefono': '3001234567',
        'estado': 'activo',
        'contrasena': 'cliente123',
    })
    assert response.status_code == 302
    assert Cliente.objects.filter(email='juan@test.com').exists()


def test_crear_cliente_sin_nombre(admin_client, db):
    response = admin_client.post('/admin/clientes/guardar/', {
        'email': 'sin_nombre@test.com',
        'estado': 'activo',
    })
    assert response.status_code == 200


def test_eliminar_cliente(admin_client, cliente_obj):
    pk = cliente_obj.pk
    response = admin_client.get(f'/admin/clientes/eliminar/{pk}/')
    assert response.status_code == 302
    assert not Cliente.objects.filter(pk=pk).exists()


def test_eliminar_cliente_inexistente(admin_client, db):
    response = admin_client.get('/admin/clientes/eliminar/99999/')
    assert response.status_code == 404