import os
import django
import cloudinary
import cloudinary.uploader

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oksumoda.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres:lSZAJpslUNUHbpWUrNSHZeKOdNZRVGOx@trolley.proxy.rlwy.net:19075/railway'

django.setup()

from apps.productos.models import Producto

cloudinary.config(
    cloud_name='dqlkrwnie',
    api_key='569994849447823',
    api_secret='XFH2K48s_weVup1y6wwYyFahUAM',
    secure=True,
)

MEDIA_PRODUCTOS = os.path.join(os.path.dirname(__file__), 'media', 'productos')

productos = Producto.objects.all()
total = productos.count()
actualizados = 0
errores = 0

for p in productos:
    if not p.foto:
        continue
    if p.foto.startswith('http'):
        print(f"[SKIP] {p.nombre} ya tiene URL")
        continue

    ruta = os.path.join(MEDIA_PRODUCTOS, p.foto)
    if not os.path.exists(ruta):
        print(f"[ERROR] No encontrado: {p.foto}")
        errores += 1
        continue

    try:
        resultado = cloudinary.uploader.upload(
            ruta,
            folder='oksumoda/productos',
            public_id=os.path.splitext(p.foto)[0],
            overwrite=True,
            resource_type='image',
        )
        p.foto = resultado['secure_url']
        p.save()
        actualizados += 1
        print(f"[OK] {p.nombre} → {p.foto}")
    except Exception as e:
        print(f"[ERROR] {p.nombre}: {e}")
        errores += 1

print(f"\nListo: {actualizados} subidos, {errores} errores, de {total} productos.")