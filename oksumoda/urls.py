"""
URLs principales de Oksumoda.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.usuarios.views import error_404, error_403  # ← agregar

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('dashboard', RedirectView.as_view(url='/admin/dashboard/', permanent=False)),

    # Páginas de error navegables (funcionan con DEBUG=True y False)
    path('404/', lambda request: error_404(request, exception=None)),  # ← agregar
    # Auth
    path('', include('apps.usuarios.urls')),

    # Tienda pública
    path('', include('apps.productos.urls')),

    # Carrito
    path('carrito/', include('apps.carrito.urls')),

    # Panel de administración
    path('admin/', include('apps.admin_panel.urls')),

    # Reportes PDF
    path('admin/reportes/', include('apps.reportes.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.usuarios.views.error_404'