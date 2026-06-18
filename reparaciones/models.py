from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone

class Taller(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    nif = models.CharField(max_length=20, verbose_name="CIF/NIF")
    
    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.taller.nombre}"

class Cliente(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    nif = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=10)
    poblacion = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.nif})"

class Equipo(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    numero_serie = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.marca} - {self.tipo}"

class ParteReparacion(models.Model):
    ESTADOS = [('recibido', 'Recibido'), ('diagnostico', 'En Diagnóstico'), ('esperando', 'Esperando Repuesto'), ('reparado', 'Reparado'), ('entregado', 'Entregado')]
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    descripcion_falla = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='recibido')
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    descripcion_tecnico = models.TextField(blank=True, null=True)
    horas_trabajo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    precio_hora = models.DecimalField(max_digits=6, decimal_places=2, default=30.00)
    stock_procesado = models.BooleanField(default=False)

    def __str__(self):
        return f"Parte #{self.id} - {self.equipo.marca}"

class Pieza(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    referencia = models.CharField(max_length=50)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"

class PiezaReparacion(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    parte = models.ForeignKey(ParteReparacion, on_delete=models.CASCADE, related_name='items_piezas')
    pieza = models.ForeignKey(Pieza, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

class Venta(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    parte_reparacion = models.OneToOneField(ParteReparacion, on_delete=models.SET_NULL, null=True, blank=True)
    importe_entregado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        # Representación mejorada para el listado del admin
        fecha_str = self.fecha.strftime('%d/%m/%Y %H:%M')
        return f"Venta #{self.id} | {self.cliente.nombre} | {self.total:.2f}€ | {fecha_str}"

    @property
    def total_a_cobrar(self):
        total = 0
        if self.parte_reparacion:
            total += (self.parte_reparacion.horas_trabajo * self.parte_reparacion.precio_hora)
            for item in self.parte_reparacion.items_piezas.all():
                total += (item.cantidad * item.pieza.precio_venta)
        for extra in self.productos_extras.all():
            total += (extra.cantidad * extra.pieza.precio_venta)
        return total

    @property
    def importe_devolver(self):
        return max(0, self.importe_entregado - self.total)

    def calcular_total(self):
        self.total = self.total_a_cobrar
        self.save(update_fields=['total'])

class ProductoVendido(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='productos_extras')
    pieza = models.ForeignKey(Pieza, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

@receiver(post_save, sender=ParteReparacion)
def actualizar_stock_al_cerrar(sender, instance, **kwargs):
    if instance.estado == 'entregado' and not instance.stock_procesado:
        with transaction.atomic():
            for item in instance.items_piezas.all():
                pieza = item.pieza
                if pieza.stock >= item.cantidad:
                    pieza.stock -= item.cantidad
                    pieza.save()
            instance.stock_procesado = True
            instance.save(update_fields=['stock_procesado'])
class ArqueoCaja(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    efectivo_apertura = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    efectivo_cierre_real = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ventas_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def saldo_teorico(self):
        return self.efectivo_apertura + self.total_ventas_efectivo

    @property
    def diferencia(self):
        return self.efectivo_cierre_real - self.saldo_teorico

    def __str__(self):
        return f"Arqueo {self.fecha} - {self.taller.nombre}"            