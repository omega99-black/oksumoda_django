"""
apps/categorias/models.py — equivalente a entity/Categoria.java
apps/clientes/models.py   — equivalente a entity/Cliente.java
"""

# ─── categorias ────────────────────────────────────────────────────────────
from django.db import models


class Categoria(models.Model):
    """
    Equivalente a entity/Categoria.java
    Tabla: categorias
    """
    id_categoria = models.AutoField(primary_key=True, db_column='id_categoria')
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'categorias'
        managed = True

    def __str__(self):
        return self.nombre

    @classmethod
    def filtrar(cls, nombre=None):
        qs = cls.objects.all()
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)
        return qs
