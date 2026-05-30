"""
apps/carrito/context_processors.py

Equivalente al model.addAttribute("cantidadItems", carritoService.obtenerCantidadItems())
que aparece en cada método del IndexController.
Con un context processor, el dato se inyecta automáticamente en TODAS las plantillas.
"""

from .services import obtener_cantidad_items


def carrito_context(request):
    """Inyecta cantidadItems en todos los templates (equivalente al model.addAttribute global)."""
    if request.user.is_authenticated:
        cantidad = obtener_cantidad_items(request.session)
    else:
        cantidad = 0
    return {'cantidadItems': cantidad}
