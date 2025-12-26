from django.urls import path
from .views import (
    SalesReportView, InventoryReportView,
    ProfitReportView, DashboardStatsView
)

urlpatterns = [
    path('sales/', SalesReportView.as_view(), name='sales-report'),
    path('inventory/', InventoryReportView.as_view(), name='inventory-report'),
    path('profit/', ProfitReportView.as_view(), name='profit-report'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
