from django.urls import path
from .auth_views import login, logout, me, register

urlpatterns = [
    path('login/', login, name='auth-login'),
    path('logout/', logout, name='auth-logout'),
    path('me/', me, name='auth-me'),
    path('register/', register, name='auth-register'),
]
