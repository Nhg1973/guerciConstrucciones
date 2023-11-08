# Generated by Django 4.2.7 on 2023-11-07 13:05

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_pagos_delete_pago_alter_ordendecompra_pagos'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='costo',
            field=models.DecimalField(decimal_places=2, max_digits=10, default=0.00),
        ),

        migrations.AddField(
            model_name='servicio',
            name='fecha_contratacion',
            field=models.DateField(default=datetime.datetime(2023, 11, 7, 13, 5, 25, 396845, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicio',
            name='fecha_pago',
            field=models.DateField(default=datetime.datetime(2023, 11, 7, 13, 5, 35, 353563, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicio',
            name='fecha_prestacion',
            field=models.DateField(default=datetime.datetime(2023, 11, 7, 13, 5, 40, 98907, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pagos',
            name='tipo_pago',
            field=models.CharField(blank=True, choices=[('efectivo', 'Efectivo'), ('cheque', 'Cheque'), ('facturado', 'facturado'), ('estimado', 'estimado')], max_length=100, null=True),
        ),
    ]