from django.urls import path
from .views import (
    dashboard_overview,
    inventory_analytics,
    sales_analytics,
    customer_analytics,
    dashboard_view
)

urlpatterns = [
    path('', dashboard_view, name='dashboard-view'),
    path('overview/', dashboard_overview, name='dashboard-overview'),
    path('inventory/', inventory_analytics, name='dashboard-inventory'),
    path('sales/', sales_analytics, name='dashboard-sales'),
    path('customers/', customer_analytics, name='dashboard-customers'),
]
