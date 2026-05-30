from django.shortcuts import render, get_object_or_404
from .models import Producto


def inicio(request):
    return render(request, 'Inicio.html')


def hombres(request):
    request.session['pagina_anterior'] = '/hombres/'
    productos = Producto.objects.filter(categoria='Hombres', estado='activo')
    return render(request, 'hombres.html', {'productos': productos})


def mujeres(request):
    request.session['pagina_anterior'] = '/mujeres/'
    productos = Producto.objects.filter(categoria='Mujeres', estado='activo')
    return render(request, 'mujeres.html', {'productos': productos})


def ninos(request):
    request.session['pagina_anterior'] = '/ninos/'
    productos = Producto.objects.filter(categoria='Niños', estado='activo')
    return render(request, 'ninos.html', {'productos': productos})


def otros(request):
    request.session['pagina_anterior'] = '/otros/'
    productos = Producto.objects.filter(categoria='Otros', estado='activo')
    return render(request, 'otros.html', {'productos': productos})


def buscar(request):
    query = request.GET.get('q', '').strip()
    productos = []
    if query:
        productos = Producto.objects.filter(
            nombre__icontains=query,
            estado='activo'
        )
    return render(request, 'buscar.html', {
        'productos': productos,
        'query': query,
    })


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, estado='activo')
    return render(request, 'detalle_producto.html', {
        'producto': producto,
        'colores': producto.get_colores_list(),
        'tallas': producto.get_tallas_list(),
    })


def error_404(request):
    return render(request, '404.html', status=404)


def error_403(request):
    return render(request, '403.html', status=403)


def contactanos(request):
    return render(request, 'contactanos.html')