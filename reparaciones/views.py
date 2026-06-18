from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from .models import ParteReparacion, Venta, Pieza, ArqueoCaja

def imprimir_ticket(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'tickets/ticket_template.html', {'venta': venta})

def es_tecnico(user):
    return user.groups.filter(name='Tecnico').exists()

@login_required
@user_passes_test(es_tecnico)
def panel_tecnico(request):
    taller = request.user.perfil.taller
    partes = ParteReparacion.objects.filter(taller=taller).exclude(estado='entregado')
    return render(request, 'tecnico/panel.html', {'partes': partes})

@login_required
def arqueo_caja(request):
    hoy = timezone.now().date()
    taller = request.user.perfil.taller
    ventas_hoy = Venta.objects.filter(taller=taller, fecha__date=hoy)
    total_ventas = ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0
    
    arqueo, created = ArqueoCaja.objects.get_or_create(
        taller=taller, fecha=hoy,
        defaults={'efectivo_apertura': 0, 'total_ventas_efectivo': total_ventas}
    )
    
    # Lógica de bloqueo: 
    # Bloqueamos edición si el cierre ya tiene valor Y el usuario no tiene permiso especial ni es superusuario
    permiso_edicion = request.user.is_superuser or request.user.has_perm('reparaciones.change_arqueocaja')
    es_cerrado = arqueo.efectivo_cierre_real > 0 and not permiso_edicion

    if request.method == 'POST' and not es_cerrado:
        def safe_decimal(valor):
            try: return Decimal(valor)
            except (InvalidOperation, ValueError, TypeError): return Decimal('0')

        arqueo.efectivo_apertura = safe_decimal(request.POST.get('efectivo_apertura'))
        arqueo.efectivo_cierre_real = safe_decimal(request.POST.get('efectivo_real'))
        arqueo.total_ventas_efectivo = total_ventas
        arqueo.save()
        return redirect('/admin/')
    
    elif not es_cerrado and arqueo.total_ventas_efectivo != total_ventas:
        arqueo.total_ventas_efectivo = total_ventas
        arqueo.save()
    
    return render(request, 'admin/arqueo.html', {
        'arqueo': arqueo,
        'ventas': ventas_hoy,
        'fecha': hoy,
        'es_cerrado': es_cerrado
    })

@login_required
def historial_arqueos(request):
    taller = request.user.perfil.taller
    historial = ArqueoCaja.objects.filter(taller=taller).order_by('-fecha')
    return render(request, 'admin/historial_arqueos.html', {'historial': historial})

@login_required
def informe_stock_critico(request):
    minimo = int(request.GET.get('minimo', 5))
    taller = request.user.perfil.taller
    piezas_criticas = Pieza.objects.filter(taller=taller, stock__lte=minimo)
    return render(request, 'admin/stock_critico.html', {'piezas': piezas_criticas, 'minimo': minimo})