from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Taller, Cliente, Equipo, ParteReparacion, Pieza, PiezaReparacion, Venta, ProductoVendido, PerfilUsuario, ArqueoCaja

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
        # Asignación forzosa antes de guardar
        if not request.user.is_superuser:
            try:
                obj.taller = request.user.perfil.taller
            except (AttributeError, PerfilUsuario.DoesNotExist):
                pass
        super().save_model(request, obj, form, change)

    # Esto es VITAL: obliga a que los Inlines también hereden el taller del usuario
    def save_formset(self, request, form, formset, change):
        if not request.user.is_superuser:
            instances = formset.save(commit=False)
            for instance in instances:
                if hasattr(instance, 'taller'):
                    instance.taller = request.user.perfil.taller
                instance.save()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)

# --- Inlines (Añadimos TallerAdminMixin si es necesario o manejamos la lógica) ---
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

class ProductoVendidoInline(admin.TabularInline):
    model = ProductoVendido
    extra = 1
    autocomplete_fields = ['pieza']
    exclude = ('taller',)

# --- Registros ---

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'nif')

@admin.register(Pieza)
class PiezaAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('taller',)
    list_display = ('nombre', 'referencia', 'stock', 'taller')
    search_fields = ('nombre', 'referencia')

@admin.register(Equipo)
class EquipoAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('taller',)
    search_fields = ('marca', 'tipo')

@admin.register(Cliente)
class ClienteAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('taller',)
    inlines = [EquipoInline]
    list_display = ('nombre', 'nif', 'telefono')

@admin.register(ParteReparacion)
class ParteReparacionAdmin(TallerAdminMixin, admin.ModelAdmin):
    exclude = ('taller',)
    autocomplete_fields = ['equipo']
    inlines = [PiezaReparacionInline]

@admin.register(Venta)
class VentaAdmin(TallerAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total_display')
    fields = ('cliente', 'parte_reparacion', 'importe_entregado', 'total')
    readonly_fields = ('total',)
    inlines = [ProductoVendidoInline]

    def total_display(self, obj):
        return f"{obj.total:.2f}€"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calcular_total()

# --- Configuración Usuario ---
try: admin.site.unregister(User)
except admin.sites.NotRegistered: pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [PerfilInline]