"""
URLs principales de Oksumoda.
Equivalente a la configuración de rutas en Spring Security (SecurityConfig)
y los @RequestMapping de cada Controller.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Auth (equivalente a /login y /registro en AuthController)
    path('', include('apps.usuarios.urls')),

    # Tienda pública (equivalente a IndexController)
    path('', include('apps.productos.urls')),

    # Carrito (equivalente a CarritoController)
    path('carrito/', include('apps.carrito.urls')),

    # Panel de administración (equivalente a AdminController)
    path('admin/', include('apps.admin_panel.urls')),

    # Reportes PDF (equivalente a los métodos reporteXxx en AdminController)
    path('admin/reportes/', include('apps.reportes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
