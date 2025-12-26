from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentCallbackViewSet, RefundViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'callbacks', PaymentCallbackViewSet, basename='payment-callback')
router.register(r'refunds', RefundViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
    
    # Payment gateway webhooks will be added here
    path('webhooks/mpesa/', include('payments.mpesa.urls')),
    path('webhooks/airtel/', include('payments.airtel.urls')),
    path('webhooks/card/', include('payments.cards.urls')),
]
