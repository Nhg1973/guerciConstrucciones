# Generated by Django 4.2.7 on 2023-11-03 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254, null=True)),
                ('fecha_registro', models.DateField(auto_now_add=True)),
                ('representante_legal', models.CharField(blank=True, max_length=100, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254, null=True)),
                ('fecha_contratacion', models.DateField()),
                ('puesto', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_compra', models.DateField()),
                ('fecha_entrega', models.DateField()),
                ('fecha_pago', models.DateField()),
                ('transportista', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.material')),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField()),
                ('fecha_finalizacion', models.DateField()),
                ('ubicacion', models.CharField(max_length=200)),
                ('tipo_proyecto', models.CharField(choices=[('casa', 'Casa'), ('empresa', 'Empresa'), ('otro', 'Otro')], max_length=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('tiempo_ejecucion', models.PositiveIntegerField()),
                ('empleado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.empleado')),
                ('material', models.ManyToManyField(through='home.MaterialTarea', to='home.material')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.proyecto')),
                ('servicio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.servicio')),
            ],
        ),
        migrations.AddField(
            model_name='materialtarea',
            name='tarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.tarea'),
        ),
        migrations.AddField(
            model_name='material',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.proveedor'),
        ),
    ]
