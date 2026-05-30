from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.inicio,            name='inicio'),
    path('hombres/',                    views.hombres,           name='hombres'),
    path('mujeres/',                    views.mujeres,           name='mujeres'),
    path('ninos/',                      views.ninos,             name='ninos'),
    path('otros/',                      views.otros,             name='otros'),
    path('contactanos/',                views.contactanos,       name='contactanos'),
    path('buscar/',                     views.buscar,            name='buscar'),
    path('producto/<int:producto_id>/', views.detalle_producto,  name='detalle_producto'),
    path('404/',                        views.error_404,         name='error_404'),
    path('403/',                        views.error_403,         name='error_403'),
]