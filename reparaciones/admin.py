from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Taller, Cliente, Equipo, ParteReparacion, Pieza, PiezaReparacion, Venta, ProductoVendido, PerfilUsuario, ArqueoCaja

# --- Mixin para filtrar por taller y asignar automáticamente ---
class TallerAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: 
            return qs
        try: 
            return qs.filter(taller=request.user.perfil.taller)
        except (AttributeError, PerfilUsuario.DoesNotExist): 
            return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            try:
                obj.taller = request.user.perfil.taller
            except (AttributeError, PerfilUsuario.DoesNotExist):
                pass
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not request.user.is_superuser:
                try:
                    instance.taller = request.user.perfil.taller
                except (AttributeError, PerfilUsuario.DoesNotExist):
                    pass
            instance.save()
        formset.save_m2m()

# --- Inlines ---
class PerfilInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil del Usuario'

class EquipoInline(admin.TabularInline):
    model = Equipo
    extra = 0
    exclude = ('taller',)

class PiezaReparacionInline(admin.TabularInline):
    model = PiezaReparacion
    extra = 1
    autocomplete_fields = ['pieza']
    exclude = ('taller',)

class ProductoVendidoInline(admin.TabularInline):
    model = ProductoVendido
    extra = 1
    autocomplete_fields = ['pieza']
    exclude = ('taller',)

# --- Registros Administrativos ---

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'nif')

@admin.register(ArqueoCaja)
class ArqueoAdmin(TallerAdminMixin, admin.ModelAdmin):
    list_display = ('fecha', 'efectivo_apertura', 'total_ventas_efectivo', 'efectivo_cierre_real', 'diferencia')
    list_filter = ('fecha',)
    ordering = ('-fecha',)

@admin.register(Pieza)
class PiezaAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('taller',)
    list_display = ('nombre', 'referencia', 'stock', 'taller')
    search_fields = ('nombre', 'referencia')

@admin.register(Equipo)
class EquipoAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('t