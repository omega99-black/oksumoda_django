"""
apps/admin_panel/urls.py — VERSION CORREGIDA
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal (todas las vistas por ?view=)
    path('dashboard/',               views.dashboard,            name='admin_dashboard'),

    # APIs JSON para polling y gráficas
    path('api/reportes/',            views.api_reportes,         name='api_reportes'),
    path('api/ventas-detalle/',      views.api_ventas_detalle,   name='api_ventas_detalle'),

    # Productos
    path('productos/guardar/',           views.guardar_producto,   name='guardar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto,  name='eliminar_producto'),

    # Usuarios
    path('usuarios/guardar/',            views.guardar_usuario,    name='guardar_usuario'),
    path('usuarios/eliminar/<int:pk>/',  views.eliminar_usuario,   name='eliminar_usuario'),

    # Categorías
    path('categorias/guardar/',           views.guardar_categoria,  name='guardar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),

    # Clientes
    path('clientes/guardar/',            views.guardar_cliente,    name='guardar_cliente'),
    path('clientes/eliminar/<int:pk>/',  views.eliminar_cliente,   name='eliminar_cliente'),
]