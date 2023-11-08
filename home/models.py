from django.utils import timezone
from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(blank=True, null=True)
    cuit = models.CharField(max_length=15)
    fecha_registro = models.DateField(auto_now_add=True)
    representante_legal = models.CharField(max_length=100, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class Proyecto(models.Model):
    TIPOS_DE_PROYECTO = [
        ('casa', 'Casa'),
        ('empresa', 'Empresa'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    ubicacion = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_proyecto = models.CharField(max_length=10, choices=TIPOS_DE_PROYECTO)

    def __str__(self):
        return self.nombre
    


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(blank=True, null=True)
    fecha_contratacion = models.DateField()
    puesto = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Asegúrate de que esté definido como DecimalField
    fecha_contratacion = models.DateField(default=timezone.now)  # Asegúrate de que esté definido como DateField
    fecha_prestacion = models.DateField()
    fecha_pago = models.DateField()

    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateField()
    fecha_entrega = models.DateField()
    fecha_pago = models.DateField()
    transportista = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, blank=True, null=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, blank=True, null=True)
    material = models.ManyToManyField(Material, through='MaterialTarea')
    tiempo_ejecucion = models.PositiveIntegerField()  # Tiempo en horas
    
    def __str__(self):
        return self.nombre

class MaterialTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()


class EtapaProyecto(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_estimada_finalizacion = models.DateField(null=True, blank=True)
    fecha_real_finalizacion = models.DateField(null=True, blank=True)
    porcentaje_pago = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monto_modificado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numero_certificado = models.CharField(max_length=100, null=True, blank=True)
    documento_cliente = models.FileField(upload_to='documentos_clientes/', null=True, blank=True)

    def __str__(self):
        return self.nombre


class Pagos(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_recepcion = models.DateField(null=True, blank=True)
    causa = models.TextField(null=True, blank=True)
    tipo_pago = models.CharField(max_length=100, choices=[("efectivo", "Efectivo"), ("cheque", "Cheque"),("facturado","facturado"),("estimado","estimado")], null=True, blank=True)
    
    # Campos específicos para pagos con cheque
    fecha_pago_cheque = models.DateField(null=True, blank=True)
    datos_cheque = models.TextField(null=True, blank=True)
    costo_cheque = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Relaciones con EtapaProyecto y Proveedor
    etapa_proyecto = models.ForeignKey(EtapaProyecto, on_delete=models.CASCADE, related_name='pagos_recibidos', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='pagos_realizados', null=True, blank=True)

    def __str__(self):
        return f'Pago de {self.monto}'



class OrdenDeCompra(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    monto_contratacion = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = models.CharField(max_length=100)  # Puedes personalizar este campo según tus necesidades
    etapas_proyecto = models.ManyToManyField(EtapaProyecto, related_name='ordenes_compra')
    pagos = models.ManyToManyField(Pagos, related_name='ordenes_compra')

    def __str__(self):
        return f'Orden de Compra para {self.proyecto.nombre}'