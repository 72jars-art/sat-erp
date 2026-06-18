from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Taller, Cliente, Equipo, ParteReparacion, Pieza, PiezaReparacion, Venta, ProductoVendido, PerfilUsuario, ArqueoCaja

# --- Mixin mejorado ---
class TallerAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: 
            return qs
        
        # Filtro especial para el modelo User
        if self.model == User:
            return qs.filter(perfil__taller=request.user.perfil.taller)
        
        # Filtro normal para modelos que tienen ForeignKey a Taller
        try: 
            return qs.filter(taller=request.user.perfil.taller)
        except (AttributeError, PerfilUsuario.DoesNotExist): 
            return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and hasattr(obj, 'taller'):
            try:
                obj.taller = request.user.perfil.taller
            except (AttributeError, PerfilUsuario.DoesNotExist):
                pass
        super().save_model(request, obj, form, change)

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

class ProductoVendidoInline(admin.TabularInline):
    model = ProductoVendido
    extra = 1
    autocomplete_fields = ['pieza']
    exclude = ('taller',)

# --- Registros ---

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'nif')

@admin.register(ArqueoCaja)
class ArqueoAdmin(TallerAdminMixin, admin.ModelAdmin):
    list_display = ('fecha', 'efectivo_apertura', 'total_ventas_efectivo', 'efectivo_cierre_real', 'diferencia')
    list_filter = ('fecha',)
    ordering = ('-fecha',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

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
    change_form_template = 'admin/reparaciones/venta/change_form.html'
    list_display = ('id', 'cliente', 'fecha', 'total_display')
    fields = ('cliente', 'parte_reparacion', 'importe_entregado', 'total')
    readonly_fields = ('total',)
    inlines = [ProductoVendidoInline]

    def total_display(self, obj):
        return f"{obj.total:.2f}€"
    total_display.short_description = 'Total'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calcular_total()

    def save_formset(self, request, form, formset, change):
        formset.save()
        form.instance.calcular_total()

# --- Configuración Usuario ---
try: admin.site.unregister(User)
except admin.sites.NotRegistered: pass

@admin.register(User)
class UserAdmin(TallerAdminMixin, BaseUserAdmin):
    inlines = [PerfilInline] # Integra el perfil para que no falte el taller
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')