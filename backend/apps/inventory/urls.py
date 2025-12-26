from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockMovementViewSet, StockAlertViewSet, StockCountViewSet

router = DefaultRouter()
router.register(r'movements', StockMovementViewSet, basename='stock-movement')
router.register(r'alerts', StockAlertViewSet, basename='stock-alert')
router.register(r'counts', StockCountViewSet, basename='stock-count')

urlpatterns = [
    path('', include(router.urls)),
]
