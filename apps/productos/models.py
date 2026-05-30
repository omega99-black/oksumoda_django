"""
apps/productos/models.py

Equivalente a entity/Producto.java
Tabla: productos — misma estructura de BD.
"""

from django.db import models
from decimal import Decimal


class Producto(models.Model):
    """
    Mapeo de campos Java → Python:
      id (id_producto)  → id_producto  (PK)
      nombre            → nombre
      descripcion       → descripcion
      foto              → foto
      estado            → estado
      precio            → precio
      stock (cantidad_stock) → stock
      categoria         → categoria
      subcategoria      → subcategoria
      colores           → colores      ("Negro,Blanco,Azul")
      tallas            → tallas       ("S,M,L,XL")
      precioAnterior    → precio_anterior
      esNuevo           → es_nuevo
    """

    id_producto = models.AutoField(primary_key=True, db_column='id_producto')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=20, default='activo')
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0, db_column='cantidad_stock')

    # Campos nuevos para carrito
    categoria = models.CharField(max_length=100, blank=True, null=True)
    subcategoria = models.CharField(max_length=100, blank=True, null=True)
    colores = models.CharField(max_length=200, blank=True, null=True)
    tallas = models.CharField(max_length=200, blank=True, null=True)
    precio_anterior = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        db_column='precioAnterior'
    )
    es_nuevo = models.BooleanField(default=False, db_column='esNuevo')

    class Meta:
        db_table = 'productos'
        managed = True

    def __str__(self):
        return self.nombre

    # ── Helpers equivalentes a getColoresList() / getTallasList() ──
    def get_colores_list(self):
        if self.colores:
            return [c.strip() for c in self.colores.split(',')]
        return []

    def get_tallas_list(self):
        if self.tallas:
            return [t.strip() for t in self.tallas.split(',')]
        return []

    # ── Equivalente a filtrarProductos() en ProductoService ──
    @classmethod
    def filtrar(cls, nombre=None, estado=None, precio_min=None,
                precio_max=None, stock_min=None):
        qs = cls.objects.all()
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)
        if estado:
            qs = qs.filter(estado__iexact=estado)
        if precio_min is not None:
            qs = qs.filter(precio__gte=precio_min)
        if precio_max is not None:
            qs = qs.filter(precio__lte=precio_max)
        if stock_min is not None:
            qs = qs.filter(stock__gte=stock_min)
        return qs
