from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from core.payment import (
    create_payment_intent as create_stripe_payment_intent,
    create_subscription as create_stripe_subscription,
    create_crypto_payment as create_stripe_crypto_payment,
    check_payment_status as check_stripe_payment_status,
    stripe_webhook as handle_stripe_webhook,
    get_payment_method_types as get_stripe_payment_method_types
)

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        result = create_stripe_payment_intent(
            amount=data.get('amount'),
            currency=data.get('currency'),
            artworkId=data.get('artworkId'),
            paymentMethod=data.get('paymentMethod')
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_subscription(request):
    try:
        data = json.loads(request.body)
        result = create_stripe_subscription(
            priceId=data.get('priceId'),
            paymentMethodId=data.get('paymentMethodId')
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def create_crypto_payment(request):
    try:
        data = json.loads(request.body)
        result = create_stripe_crypto_payment(
            amount=data.get('amount'),
            currency=data.get('currency'),
            artworkId=data.get('artworkId'),
            cryptoCurrency=data.get('cryptoCurrency')
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def check_payment_status(request, payment_id):
    try:
        result = check_stripe_payment_status(payment_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    try:
        result = handle_stripe_webhook(request)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_payment_method_types(request):
    try:
        payment_method = request.GET.get('method', 'card')
        result = get_stripe_payment_method_types(payment_method)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
