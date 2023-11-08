from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.utils import timezone
from .models import Pagos, Servicio, Material
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth
from django.db.models import Count
import json


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')  # Redirige al usuario a la página de bienvenida después de registrarse
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



@login_required
def welcome(request):
    # Obtener el mes y el año actuales
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    # Calcular la fecha de inicio y fin del mes actual
    primer_dia_mes_actual = timezone.datetime(anio_actual, mes_actual, 1)
    ultimo_dia_mes_actual = primer_dia_mes_actual + timezone.timedelta(days=32)

    #FACTURADO
    # Calcular la fecha de inicio y fin del mes anterior
    mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
    anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1
    primer_dia_mes_anterior = timezone.datetime(anio_anterior, mes_anterior, 1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timezone.timedelta(days=1)

    # Realizar la consulta para obtener el monto correspondiente al mes actual y tipo_pago "facturado"
    monto_mes_actual_facturado = Pagos.objects.filter(
        tipo_pago="facturado",
        fecha_recepcion__gte=primer_dia_mes_actual,
        fecha_recepcion__lt=ultimo_dia_mes_actual
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    # Realizar la consulta para obtener el monto del mes anterior y tipo_pago "facturado"
    monto_mes_anterior_facturado = Pagos.objects.filter(
        tipo_pago="facturado",
        fecha_recepcion__gte=primer_dia_mes_anterior,
        fecha_recepcion__lt=ultimo_dia_mes_anterior
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    # Calcular el porcentaje de aumento
    if monto_mes_anterior_facturado == 0:
        porcentaje_aumento = 0
    else:
        porcentaje_aumento = ((monto_mes_actual_facturado - monto_mes_anterior_facturado) / monto_mes_anterior_facturado) * 100


    #ESTIMADO
    # Realizar la consulta para obtener el monto correspondiente al mes actual y tipo_pago "estimado"
    monto_mes_actual_estimado = Pagos.objects.filter(
        tipo_pago="estimado",
        fecha_recepcion__gte=primer_dia_mes_actual,
        fecha_recepcion__lt=ultimo_dia_mes_actual
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    # Realizar la consulta para obtener el monto del mes anterior y tipo_pago "estimado"
    monto_mes_anterior_estimado = Pagos.objects.filter(
        tipo_pago="estimado",
        fecha_recepcion__gte=primer_dia_mes_anterior,
        fecha_recepcion__lt=ultimo_dia_mes_anterior
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    # Calcular el porcentaje de aumento
    if monto_mes_anterior_estimado == 0:
        porcentaje_estimado_aumento = 0
    else:
        porcentaje_estimado_aumento = ((monto_mes_actual_estimado - monto_mes_anterior_estimado) / monto_mes_anterior_estimado) * 100


    #Gasto
    # Filtra los servicios y materiales del mes actual y del mes anterior
    servicios_del_mes_actual = Servicio.objects.filter(
        fecha_contratacion__month=mes_actual,
        fecha_contratacion__year=anio_actual
    )
    materiales_del_mes_actual = Material.objects.filter(
        fecha_compra__month=mes_actual,
        fecha_compra__year=anio_actual
    )

    servicios_del_mes_anterior = Servicio.objects.filter(
        fecha_contratacion__month= mes_anterior,
        fecha_contratacion__year= anio_anterior
    )
    materiales_del_mes_anterior = Material.objects.filter(
        fecha_compra__month= mes_anterior,
        fecha_compra__year= anio_anterior
    )

    # Calcula el costo total del mes actual y del mes anterior
    costo_total_servicios_mes_actual = servicios_del_mes_actual.aggregate(
        total_costo_servicios=Sum('costo')
    )['total_costo_servicios'] or 0
    costo_total_materiales_mes_actual = materiales_del_mes_actual.aggregate(
        total_costo_materiales=Sum('costo')
    )['total_costo_materiales'] or 0

    costo_total_servicios_mes_anterior = servicios_del_mes_anterior.aggregate(
        total_costo_servicios=Sum('costo')
    )['total_costo_servicios'] or 0
    costo_total_materiales_mes_anterior = materiales_del_mes_anterior.aggregate(
        total_costo_materiales=Sum('costo')
    )['total_costo_materiales'] or 0

    # Calcula el costo total del mes actual
    costo_total_mes_actual = costo_total_servicios_mes_actual + costo_total_materiales_mes_actual

    # Calcula el costo total del mes anterior
    costo_total_mes_anterior = costo_total_servicios_mes_anterior + costo_total_materiales_mes_anterior

    # Calcula el porcentaje de cambio
    if costo_total_mes_anterior != 0:
        porcentaje_cambio = ((costo_total_mes_actual - costo_total_mes_anterior) / costo_total_mes_anterior) * 100
    else:
        porcentaje_cambio = 0


    #GRAFICO
    # Crea una lista para almacenar los totales mensuales de facturado
    mensuales_facturado = []

    # Crea una lista para almacenar los totales mensuales de estimado
    mensuales_estimado = []

    # Itera a través de los meses de enero a diciembre
    for mes in range(1, 13):
        # Filtra los pagos para el mes y año corriente con tipo_pago="facturado"
        pagos_mensuales_facturado = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion__month=mes,
            fecha_recepcion__year=anio_actual,
        )
        
        # Filtra los pagos para el mes y año corriente con tipo_pago="estimado"
        pagos_mensuales_estimado = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion__month=mes,
            fecha_recepcion__year=anio_actual,
        )
        
        # Suma los montos de los pagos mensuales con tipo_pago="facturado" y convierte el resultado en entero
        total_mensual_facturado = pagos_mensuales_facturado.aggregate(total=Sum('monto'))['total'] or 0
        total_mensual_facturado = int(total_mensual_facturado)
        
        # Suma los montos de los pagos mensuales con tipo_pago="estimado" y convierte el resultado en entero
        total_mensual_estimado = pagos_mensuales_estimado.aggregate(total=Sum('monto'))['total'] or 0
        total_mensual_estimado = int(total_mensual_estimado)
        
        # Agrega los totales mensuales a las listas respectivas
        mensuales_facturado.append(total_mensual_facturado)
        mensuales_estimado.append(total_mensual_estimado)

        # Para la clase Servicio
        costo_servicio_mensual = Servicio.objects.filter(fecha_contratacion__year=anio_actual).annotate(
            month=ExtractMonth('fecha_contratacion')
        ).values('month').annotate(total_costo=Sum('costo')).order_by('month')

        # Para la clase Material
        costo_material_mensual = Material.objects.filter(fecha_compra__year=anio_actual).annotate(
            month=ExtractMonth('fecha_compra')
        ).values('month').annotate(total_costo=Sum('costo')).order_by('month')

        # Para la clase Servicio
        mensuales_costo_servicio = [0] * 12  # Inicializa una lista con 12 ceros para cada mes

        for servicio in costo_servicio_mensual:
            mes = servicio['month']
            total_costo = servicio['total_costo']
            total_costo = int(total_costo)  # Convierte a entero
            mensuales_costo_servicio[mes - 1] = total_costo  # Resta 1 para ajustar a índices de lista (enero=0, febrero=1, etc.)

        # Para la clase Material
        mensuales_costo_material = [0] * 12  # Inicializa una lista con 12 ceros para cada mes

        for material in costo_material_mensual:
            mes = material['month']
            total_costo = material['total_costo']
            total_costo = int(total_costo)  # Convierte a entero
            mensuales_costo_material[mes - 1] = total_costo  # Resta 1 para ajustar a índices de lista (enero=0, febrero=1, etc.)


    return render(request, 'registration/welcome.html', {'datos': monto_mes_actual_facturado, 
                                                         'porcentaje_aumento': porcentaje_aumento,
                                                         'porcentaje_estimado' : porcentaje_estimado_aumento,
                                                         'estimado' : monto_mes_actual_estimado,
                                                         'costo_total_mes': costo_total_mes_actual,
                                                         'porcentaje_costo' : porcentaje_cambio,
                                                         'facturado_por_mes' : mensuales_facturado,
                                                         'estimado_por_mes' : mensuales_estimado,
                                                         'gasto_materiales_por_mes' : mensuales_costo_material,
                                                         'gasto_servi_por_mes' : mensuales_costo_servicio })




@login_required
def obtener_facturacion(request, periodo):
    # Obtener la fecha actual
    # Obtener el mes y el año actuales
    fecha_actual = timezone.now()
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    if periodo == "mes":
        # Calcular la fecha de inicio y fin del mes actual
        primer_dia_mes_actual = timezone.datetime(anio_actual, mes_actual, 1)
        ultimo_dia_mes_actual = primer_dia_mes_actual + timezone.timedelta(days=32)

        # Calcular la fecha de inicio y fin del mes anterior
        mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
        anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1
        primer_dia_mes_anterior = timezone.datetime(anio_anterior, mes_anterior, 1)
        ultimo_dia_mes_anterior = primer_dia_mes_actual - timezone.timedelta(days=1)

        # Realizar la consulta para obtener el monto correspondiente al mes actual y tipo_pago "facturado"
        total = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion__gte=primer_dia_mes_actual,
            fecha_recepcion__lt=ultimo_dia_mes_actual
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Realizar la consulta para obtener el monto del mes anterior y tipo_pago "facturado"
        monto_mes_anterior_facturado = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion__gte=primer_dia_mes_anterior,
            fecha_recepcion__lt=ultimo_dia_mes_anterior
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if monto_mes_anterior_facturado == 0:
            ganancia = 0
        else:
            ganancia = round(((total - monto_mes_anterior_facturado) / monto_mes_anterior_facturado) * 100, 2)

    
    elif periodo == "hoy":
        # Calcular los datos de facturación para el día actual en comparación con el día anterior
        fecha_hoy = timezone.now().date()  # Obtener solo la fecha sin la hora
    
        fecha_ayer = fecha_hoy - timezone.timedelta(days=1)  # Calcular la fecha de ayer

        facturacion_hoy = Pagos.objects.filter(
                tipo_pago="facturado",
                fecha_recepcion=fecha_hoy
            ).aggregate(Sum('monto'))['monto__sum'] or 0

        facturacion_ayer = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion=fecha_ayer
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if facturacion_ayer == 0:
            ganancia = 0
        else:
            ganancia = round(((facturacion_hoy - facturacion_ayer) / facturacion_ayer) * 100, 2)

        total = facturacion_hoy

    elif periodo == "anual":
        # Calcular la fecha de inicio y fin del año actual
        primer_dia_anio_actual = timezone.datetime(fecha_actual.year, 1, 1)
        ultimo_dia_anio_actual = timezone.datetime(fecha_actual.year, 12, 31)

        # Calcular la fecha de inicio y fin del año anterior
        anio_anterior = fecha_actual.year - 1
        primer_dia_anio_anterior = timezone.datetime(anio_anterior, 1, 1)
        ultimo_dia_anio_anterior = timezone.datetime(anio_anterior, 12, 31)

        # Realizar consultas para obtener la facturación del año actual y la del año anterior
        facturacion_anio_actual = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion__gte=primer_dia_anio_actual,
            fecha_recepcion__lte=ultimo_dia_anio_actual
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        facturacion_anio_anterior = Pagos.objects.filter(
            tipo_pago="facturado",
            fecha_recepcion__gte=primer_dia_anio_anterior,
            fecha_recepcion__lte=ultimo_dia_anio_anterior
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if facturacion_anio_anterior == 0:
            ganancia = 0
        else:
            ganancia = round(((facturacion_anio_actual - facturacion_anio_anterior) / facturacion_anio_anterior) * 100, 2)

        total = facturacion_anio_actual 
    else:
        return JsonResponse({"error": "Período de facturación no válido"})

    datos = {"total": total, "ganancia": ganancia}

    try:
        # Realiza cálculos y obtén los datos
        datos = {"total": total, "ganancia": ganancia}
        return JsonResponse(datos)
    except Exception as e:
        # Maneja el error y devuelve una respuesta JSON de error
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def obtener_estimado(request, periodo):
    # Obtener la fecha actual
    # Obtener el mes y el año actuales
    fecha_actual = timezone.now()
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    if periodo == "mes":
        # Calcular la fecha de inicio y fin del mes actual
        primer_dia_mes_actual = timezone.datetime(anio_actual, mes_actual, 1)
        ultimo_dia_mes_actual = primer_dia_mes_actual + timezone.timedelta(days=32)

        # Calcular la fecha de inicio y fin del mes anterior
        mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
        anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1
        primer_dia_mes_anterior = timezone.datetime(anio_anterior, mes_anterior, 1)
        ultimo_dia_mes_anterior = primer_dia_mes_actual - timezone.timedelta(days=1)

        # Realizar la consulta para obtener el monto correspondiente al mes actual y tipo_pago "facturado"
        total = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion__gte=primer_dia_mes_actual,
            fecha_recepcion__lt=ultimo_dia_mes_actual
        ).aggregate(Sum('monto'))['monto__sum'] or 0


        # Realizar la consulta para obtener el monto del mes anterior y tipo_pago "facturado"
        monto_mes_anterior_facturado = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion__gte=primer_dia_mes_anterior,
            fecha_recepcion__lt=ultimo_dia_mes_anterior
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if monto_mes_anterior_facturado == 0:
            ganancia = 0
        else:
            ganancia = round(((total - monto_mes_anterior_facturado) / monto_mes_anterior_facturado) * 100, 2)

    
    elif periodo == "hoy":
        # Calcular los datos de facturación para el día actual en comparación con el día anterior
        fecha_hoy = timezone.now().date()  # Obtener solo la fecha sin la hora
    
        fecha_ayer = fecha_hoy - timezone.timedelta(days=1)  # Calcular la fecha de ayer

        facturacion_hoy = Pagos.objects.filter(
                tipo_pago="estimado",
                fecha_recepcion=fecha_hoy
            ).aggregate(Sum('monto'))['monto__sum'] or 0

        facturacion_ayer = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion=fecha_ayer
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if facturacion_ayer == 0:
            ganancia = 0
        else:
            ganancia = round(((facturacion_hoy - facturacion_ayer) / facturacion_ayer) * 100, 2)

        total = facturacion_hoy

    elif periodo == "anual":
        # Calcular la fecha de inicio y fin del año actual
        primer_dia_anio_actual = timezone.datetime(fecha_actual.year, 1, 1)
        ultimo_dia_anio_actual = timezone.datetime(fecha_actual.year, 12, 31)

        # Calcular la fecha de inicio y fin del año anterior
        anio_anterior = fecha_actual.year - 1
        primer_dia_anio_anterior = timezone.datetime(anio_anterior, 1, 1)
        ultimo_dia_anio_anterior = timezone.datetime(anio_anterior, 12, 31)

        # Realizar consultas para obtener la facturación del año actual y la del año anterior
        facturacion_anio_actual = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion__gte=primer_dia_anio_actual,
            fecha_recepcion__lte=ultimo_dia_anio_actual
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        facturacion_anio_anterior = Pagos.objects.filter(
            tipo_pago="estimado",
            fecha_recepcion__gte=primer_dia_anio_anterior,
            fecha_recepcion__lte=ultimo_dia_anio_anterior
        ).aggregate(Sum('monto'))['monto__sum'] or 0

        # Calcular el porcentaje de aumento
        if facturacion_anio_anterior == 0:
            ganancia = 0
        else:
            ganancia = round(((facturacion_anio_actual - facturacion_anio_anterior) / facturacion_anio_anterior) * 100, 2)

        total = facturacion_anio_actual 
    else:
        return JsonResponse({"error": "Período de facturación no válido"})

    datos = {"estimado_total": total, "estimado_ganancia": ganancia}

    try:

        return JsonResponse(datos)
    except Exception as e:
        # Maneja el error y devuelve una respuesta JSON de error
        return JsonResponse({"error": str(e)}, status=500)
    



@login_required
def obtener_gasto(request, periodo):
    try:
        # Obtener la fecha actual
        fecha_actual = timezone.now()

        if periodo == "mes":
            # Obtener el mes y el año actuales
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year

            # Calcular la fecha de inicio y fin del mes actual
            primer_dia_mes_actual = timezone.datetime(anio_actual, mes_actual, 1)
            ultimo_dia_mes_actual = primer_dia_mes_actual + timedelta(days=32)

            # Calcular la fecha de inicio y fin del mes anterior
            mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
            anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1
            primer_dia_mes_anterior = timezone.datetime(anio_anterior, mes_anterior, 1)
            ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)

            # Filtrar los servicios y materiales del mes actual y del mes anterior
            servicios_mes_actual = Servicio.objects.filter(
                fecha_contratacion__range=(primer_dia_mes_actual, ultimo_dia_mes_actual)
            )
            materiales_mes_actual = Material.objects.filter(
                fecha_compra__range=(primer_dia_mes_actual, ultimo_dia_mes_actual)
            )

            servicios_mes_anterior = Servicio.objects.filter(
                fecha_contratacion__range=(primer_dia_mes_anterior, ultimo_dia_mes_anterior)
            )
            materiales_mes_anterior = Material.objects.filter(
                fecha_compra__range=(primer_dia_mes_anterior, ultimo_dia_mes_anterior)
            )

            # Calcular el costo total de servicios y materiales del mes actual y del mes anterior
            costo_total_mes_actual = round((servicios_mes_actual.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_mes_actual.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)
            costo_total_mes_anterior = round((servicios_mes_anterior.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_mes_anterior.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)

            # Calcular el porcentaje de cambio
            if costo_total_mes_anterior != 0:
                porcentaje_cambio = ((costo_total_mes_actual - costo_total_mes_anterior) / costo_total_mes_anterior) * 100
            else:
                porcentaje_cambio = 0

            datos = {
                "costo_total_actual": costo_total_mes_actual,
                "costo_total_anterior": costo_total_mes_anterior,
                "porcentaje_cambio": porcentaje_cambio
            }

        elif periodo == "hoy":
            # Calcular los datos del gasto para el día actual en comparación con el día anterior
            fecha_hoy = fecha_actual.date()  # Obtener solo la fecha sin la hora
            fecha_ayer = fecha_hoy - timedelta(days=1)  # Calcular la fecha de ayer

            servicios_hoy = Servicio.objects.filter(
                fecha_contratacion=fecha_hoy
            )
            materiales_hoy = Material.objects.filter(
                fecha_compra=fecha_hoy
            )

            servicios_ayer = Servicio.objects.filter(
                fecha_contratacion=fecha_ayer
            )
            materiales_ayer = Material.objects.filter(
                fecha_compra=fecha_ayer
            )

            costo_total_hoy = round((servicios_hoy.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_hoy.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)
            costo_total_ayer = round((servicios_ayer.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_ayer.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)

            # Calcular el porcentaje de cambio
            if costo_total_ayer != 0:
                porcentaje_cambio = ((costo_total_hoy - costo_total_ayer) / costo_total_ayer) * 100
            else:
                porcentaje_cambio = 0

            datos = {
                "costo_total_actual": costo_total_hoy,
                "costo_total_anterior": costo_total_ayer,
                "porcentaje_cambio": porcentaje_cambio
            }

        elif periodo == "anual":
            # Calcular la fecha de inicio y fin del año actual
            primer_dia_anio_actual = timezone.datetime(fecha_actual.year, 1, 1)
            ultimo_dia_anio_actual = timezone.datetime(fecha_actual.year, 12, 31)

            # Calcular la fecha de inicio y fin del año anterior
            anio_anterior = fecha_actual.year - 1
            primer_dia_anio_anterior = timezone.datetime(anio_anterior, 1, 1)
            ultimo_dia_anio_anterior = timezone.datetime(anio_anterior, 12, 31)

            servicios_anio_actual = Servicio.objects.filter(
                fecha_contratacion__range=(primer_dia_anio_actual, ultimo_dia_anio_actual)
            )
            materiales_anio_actual = Material.objects.filter(
                fecha_compra__range=(primer_dia_anio_actual, ultimo_dia_anio_actual)
            )

            servicios_anio_anterior = Servicio.objects.filter(
                fecha_contratacion__range=(primer_dia_anio_anterior, ultimo_dia_anio_anterior)
            )
            materiales_anio_anterior = Material.objects.filter(
                fecha_compra__range=(primer_dia_anio_anterior, ultimo_dia_anio_anterior)
            )

            costo_total_anio_actual = round((servicios_anio_actual.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_anio_actual.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)
            costo_total_anio_anterior = round((servicios_anio_anterior.aggregate(total_costo=Sum('costo'))['total_costo'] or 0) + (materiales_anio_anterior.aggregate(total_costo=Sum('costo'))['total_costo'] or 0), 2)

            if costo_total_anio_anterior != 0:
                porcentaje_cambio = ((costo_total_anio_actual - costo_total_anio_anterior) / costo_total_anio_anterior) * 100
            else:
                porcentaje_cambio = 0

            datos = {
                "costo_total_actual": costo_total_anio_actual,
                "costo_total_anterior": costo_total_anio_anterior,
                "porcentaje_cambio": porcentaje_cambio
            }

        else:
            return JsonResponse({"error": "Período de facturación no válido"})

        return JsonResponse(datos)

    except Exception as e:
        # Manejar el error y devolver una respuesta JSON de error
        return JsonResponse({"error": str(e)}, status=500)
