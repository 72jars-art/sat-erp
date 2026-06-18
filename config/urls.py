from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
# IMPORTANTE: Importa también historial_arqueos
from reparaciones.views import arqueo_caja, informe_stock_critico, historial_arqueos 

urlpatterns = [
    # Redirección de la raíz (/) al panel de administración
    path('', lambda request: redirect('admin:index')), 

    # Rutas personalizadas (Añadimos la del historial aquí)
    path('admin/arqueo/', arqueo_caja, name='arqueo_caja'),
    path('admin/arqueo/historial/', historial_arqueos, name='historial_arqueos'),
    path('admin/stock-critico/', informe_stock_critico, name='stock_critico'),
    
    # Ruta principal del administrador
    path('admin/', admin.site.urls),
    
    # Rutas de la aplicación reparaciones
    path('reparaciones/', include('reparaciones.urls')),
]