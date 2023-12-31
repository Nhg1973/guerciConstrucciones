# Generated by Django 4.2.7 on 2023-11-04 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_cliente_cuit'),
    ]

    operations = [
        migrations.CreateModel(
            name='EtapaProyecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_estimada_finalizacion', models.DateField(blank=True, null=True)),
                ('fecha_real_finalizacion', models.DateField(blank=True, null=True)),
                ('porcentaje_pago', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('monto_modificado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('numero_certificado', models.CharField(blank=True, max_length=100, null=True)),
                ('documento_cliente', models.FileField(blank=True, null=True, upload_to='documentos_clientes/')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_recepcion', models.DateField(blank=True, null=True)),
                ('causa', models.TextField(blank=True, null=True)),
                ('tipo_pago', models.CharField(blank=True, choices=[('efectivo', 'Efectivo'), ('cheque', 'Cheque')], max_length=100, null=True)),
                ('fecha_pago_cheque', models.DateField(blank=True, null=True)),
                ('datos_cheque', models.TextField(blank=True, null=True)),
                ('costo_cheque', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('etapa_proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos_recibidos', to='home.etapaproyecto')),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos_realizados', to='home.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='OrdenDeCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto_contratacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('forma_pago', models.CharField(max_length=100)),
                ('etapas_proyecto', models.ManyToManyField(related_name='ordenes_compra', to='home.etapaproyecto')),
                ('pagos', models.ManyToManyField(related_name='ordenes_compra', to='home.pago')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.proyecto')),
            ],
        ),
    ]
