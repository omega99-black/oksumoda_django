"""
apps/clientes/models.py
Equivalente a entity/Cliente.java
"""

from django.db import models


class Cliente(models.Model):
    """
    Tabla: clientes — misma estructura de BD.
    """
    id_cliente = models.AutoField(primary_key=True, db_column='id_cliente')
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=100, db_column='contrasena')
    estado = models.CharField(max_length=20, default='activo')

    class Meta:
        db_table = 'clientes'
        managed = True

    def __str__(self):
        return f'{self.nombre} ({self.email})'

    @classmethod
    def filtrar(cls, nombre=None, email=None, telefono=None, estado=None):
        """Equivalente a ClienteService.filtrarClientes()"""
        qs = cls.objects.all()
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)
        if email:
            qs = qs.filter(email__icontains=email)
        if telefono:
            qs = qs.filter(telefono__icontains=telefono)
        if estado:
            qs = qs.filter(estado__iexact=estado)
        return qs
