from django.urls import path
from . import auth

urlpatterns = [
    path('auth/login/', auth.login_view, name='login'),
    path('auth/logout/', auth.logout_view, name='logout'),
    path('auth/register/', auth.register_view, name='register'),
] 