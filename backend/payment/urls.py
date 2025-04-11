from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('create-crypto-payment/', views.create_crypto_payment, name='create_crypto_payment'),
    path('check-payment-status/<str:payment_id>/', views.check_payment_status, name='check_payment_status'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-methods/', views.get_payment_method_types, name='get_payment_method_types'),
] 