from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.airtel_callback, name='airtel-callback'),
]
