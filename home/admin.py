
from django.contrib import admin
from .models import Cliente, Proyecto, Tarea, Empleado, Servicio, Material, Proveedor,EtapaProyecto,OrdenDeCompra,Pagos


admin.site.register(Cliente)
admin.site.register(Proyecto)
admin.site.register(Tarea)
admin.site.register(Empleado)
admin.site.register(Servicio)
admin.site.register(Material)
admin.site.register(Proveedor)
admin.site.register(EtapaProyecto)
admin.site.register(OrdenDeCompra)
admin.site.register(Pagos)


