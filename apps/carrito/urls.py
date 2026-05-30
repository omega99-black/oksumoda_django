"""apps/carrito/urls.py"""

from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.ver_carrito, name='carrito'),
    path('agregar/',                views.agregar,     name='carrito_agregar'),
    path('eliminar/<int:producto_id>/', views.eliminar, name='carrito_eliminar'),
    path('actualizar/<int:producto_id>/', views.actualizar, name='carrito_actualizar'),
    path('cantidad/',               views.cantidad,    name='carrito_cantidad'),
    path('vaciar/',                 views.vaciar,      name='carrito_vaciar'),
    path('checkout/',               views.checkout,    name='checkout'),
]
