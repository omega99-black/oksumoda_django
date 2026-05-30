"""
apps/carrito/services.py

Equivalente a service/CarritoService.java anotado con @SessionScope.
En Django no hay @SessionScope; se almacena el carrito en request.session.
Cada método recibe el objeto `session` de Django en lugar de ser un bean.
"""

from decimal import Decimal
from apps.productos.models import Producto


CARRITO_SESSION_KEY = 'carrito'


def _get_carrito(session) -> dict:
    """
    Obtiene el carrito de la sesión.
    Estructura: {str(producto_id): {productoId, nombre, precio, cantidad, imagen, talla, color}}
    Equivalente al campo `List<CarritoItem> items` en CarritoService.
    """
    if CARRITO_SESSION_KEY not in session:
        session[CARRITO_SESSION_KEY] = {}
    return session[CARRITO_SESSION_KEY]


def _save_carrito(session, carrito: dict):
    session[CARRITO_SESSION_KEY] = carrito
    session.modified = True


# ── agregarProductoPorId() ──────────────────────────────────────────────────
def agregar_producto(session, producto_id: int, cantidad: int = 1,
                     talla: str = None, color: str = None):
    """
    Equivalente a CarritoService.agregarProductoPorId() +
                 CarritoService.agregarProducto()
    """
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        raise ValueError('Producto no encontrado')

    if producto.stock < cantidad:
        raise ValueError(f'Stock insuficiente. Disponible: {producto.stock}')

    carrito = _get_carrito(session)
    key = str(producto_id)

    if key in carrito:
        nueva_cantidad = carrito[key]['cantidad'] + cantidad
        if producto.stock < nueva_cantidad:
            raise ValueError('Stock insuficiente para la cantidad solicitada')
        carrito[key]['cantidad'] = nueva_cantidad
        print(f'✅ Cantidad actualizada: {nueva_cantidad}')
    else:
        carrito[key] = {
            'producto_id': producto.id_producto,
            'nombre':      producto.nombre,
            'precio':      str(producto.precio),   # Decimal → str para JSON
            'cantidad':    cantidad,
            'imagen':      producto.foto or '',
            'talla':       talla or '',
            'color':       color or '',
        }
        print(f'✅ Producto agregado al carrito: {producto.nombre}')

    _save_carrito(session, carrito)


# ── eliminarProducto() ──────────────────────────────────────────────────────
def eliminar_producto(session, producto_id: int):
    """Equivalente a CarritoService.eliminarProducto()"""
    carrito = _get_carrito(session)
    carrito.pop(str(producto_id), None)
    _save_carrito(session, carrito)
    print(f'✅ Producto {producto_id} eliminado del carrito')


# ── actualizarCantidad() ────────────────────────────────────────────────────
def actualizar_cantidad(session, producto_id: int, nueva_cantidad: int):
    """Equivalente a CarritoService.actualizarCantidad()"""
    if nueva_cantidad <= 0:
        eliminar_producto(session, producto_id)
        return

    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        raise ValueError('Producto no encontrado')

    if producto.stock < nueva_cantidad:
        raise ValueError(f'Stock insuficiente. Disponible: {producto.stock}')

    carrito = _get_carrito(session)
    key = str(producto_id)
    if key in carrito:
        carrito[key]['cantidad'] = nueva_cantidad
        _save_carrito(session, carrito)
        print(f'✅ Cantidad actualizada a: {nueva_cantidad}')


# ── obtenerItems() ──────────────────────────────────────────────────────────
def obtener_items(session) -> list:
    """
    Equivalente a CarritoService.obtenerItems().
    Devuelve lista de dicts (en lugar de List<CarritoItem>).
    """
    carrito = _get_carrito(session)
    items = []
    for item in carrito.values():
        item_copy = dict(item)
        precio = Decimal(item_copy['precio'])
        item_copy['precio'] = precio
        item_copy['subtotal'] = precio * item_copy['cantidad']
        items.append(item_copy)
    return items


# ── calcularTotal() ─────────────────────────────────────────────────────────
def calcular_total(session) -> Decimal:
    """Equivalente a CarritoService.calcularTotal()"""
    return sum(
        Decimal(item['precio']) * item['cantidad']
        for item in _get_carrito(session).values()
    )


# ── obtenerCantidadItems() ──────────────────────────────────────────────────
def obtener_cantidad_items(session) -> int:
    """Equivalente a CarritoService.obtenerCantidadItems()"""
    return sum(item['cantidad'] for item in _get_carrito(session).values())


# ── vaciarCarrito() ─────────────────────────────────────────────────────────
def vaciar_carrito(session):
    """Equivalente a CarritoService.vaciarCarrito()"""
    session[CARRITO_SESSION_KEY] = {}
    session.modified = True
    print('✅ Carrito vaciado')


# ── estaVacio() ─────────────────────────────────────────────────────────────
def esta_vacio(session) -> bool:
    """Equivalente a CarritoService.estaVacio()"""
    return len(_get_carrito(session)) == 0
