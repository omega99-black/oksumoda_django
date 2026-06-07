# apps/carrito/context_processors.py

from decimal import Decimal

CARRITO_SESSION_KEY = 'carrito'

def carrito_context(request):
    if not hasattr(request, 'session'):
        return {'cantidadItems': 0}
    
    try:
        # Solo leer, nunca escribir
        carrito = request.session.get(CARRITO_SESSION_KEY, {})
        cantidad = sum(item.get('cantidad', 0) for item in carrito.values())
    except Exception:
        cantidad = 0
    
    return {'cantidadItems': cantidad}