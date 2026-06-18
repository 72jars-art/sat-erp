from django.urls import path
from . import views

urlpatterns = [
    # ... (tus otras rutas existentes, ej: path('admin/...', ...))
    
    # Rutas para arqueo y gestión de caja
    path('admin/arqueo/', views.arqueo_caja, name='arqueo_caja'),
    path('admin/arqueo/historial/', views.historial_arqueos, name='historial_arqueos'),
    
    # Otras utilidades
    path('admin/stock-critico/', views.informe_stock_critico, name='informe_stock_critico'),
    path('ticket/<int:venta_id>/', views.imprimir_ticket, name='imprimir_ticket'),
]