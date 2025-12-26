from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.card_callback, name='card-callback'),
]
