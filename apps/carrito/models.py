"""
apps/carrito/models.py
"""

from django.db import models
from apps.clientes.models import Cliente
from apps.productos.models import Producto


class Venta(models.Model):
    id_venta    = models.AutoField(primary_key=True, db_column='id_venta')
    cliente     = models.ForeignKey(Cliente, on_delete=models.CASCADE,
                                    related_name='ventas', db_column='id_cliente')
    fecha_venta = models.DateTimeField(auto_now_add=True, db_column='fecha_venta')
    total_venta = models.DecimalField(max_digits=12, decimal_places=2,
                                      db_column='total_venta')
    estado      = models.CharField(max_length=50, default='completada')
    metodo_pago = models.CharField(max_length=50, default='efectivo')

    class Meta:
        db_table = 'ventas'
        managed  = True

    def __str__(self):
        return f'Venta #{self.id_venta} - {self.cliente.nombre}'


class DetalleVenta(models.Model):
    id_detalle  = models.AutoField(primary_key=True, db_column='id_detalle')
    venta       = models.ForeignKey(Venta, on_delete=models.CASCADE,
                                    related_name='detalles', db_column='id_venta')
    producto    = models.ForeignKey(Producto, on_delete=models.CASCADE,
                                    related_name='detalles_venta',
                                    db_column='id_producto')
    cantidad    = models.IntegerField()
    precio_unit = models.DecimalField(max_digits=10, decimal_places=2,
                                      db_column='precio_unit')
    subtotal    = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'detalle_ventas'
        managed  = True

    def __str__(self):
        return f'Detalle #{self.id_detalle} - {self.producto.nombre}'