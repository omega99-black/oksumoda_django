"""
apps/reportes/urls.py
Equivalente a los @GetMapping("/admin/reportes/xxx") en AdminController.java
"""

from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/',   views.reporte_usuarios,   name='reporte_usuarios'),
    path('productos/',  views.reporte_productos,  name='reporte_productos'),
    path('categorias/', views.reporte_categorias, name='reporte_categorias'),
    path('clientes/',   views.reporte_clientes,   name='reporte_clientes'),
]
