import os
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Verifica che la chiave Stripe esista
if not hasattr(settings, 'STRIPE_SECRET_KEY'):
    raise ValueError('Missing STRIPE_SECRET_KEY in settings')

# Inizializza Stripe con la chiave segreta
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    """
    Crea un payment intent per un pagamento una tantum
    """
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        artwork_id = data.get('artworkId')
        payment_method = data.get('paymentMethod', 'card')

        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)

        amount_in_cents = int(float(amount) * 100)
        
        # Opzioni di pagamento in base al metodo selezionato
        payment_method_types = get_payment_method_types(payment_method)

        payment_intent_data = {
            'amount': amount_in_cents,
            'currency': currency,
            'payment_method_types': payment_method_types,
            'metadata': {
                'artwork_id': str(artwork_id) if artwork_id else None,
                'user_id': str(request.user.id) if request.user.is_authenticated else None,
            }
        }

        # Crea il payment intent
        payment_intent = stripe.PaymentIntent.create(**payment_intent_data)

        return JsonResponse({
            'clientSecret': payment_intent.client_secret,
            'id': payment_intent.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_subscription(request):
    """
    Crea una sottoscrizione per l'utente corrente
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        price_id = data.get('priceId')
        plan_type = data.get('planType')
        
        user = request.user
        
        # Se l'utente ha già una sottoscrizione attiva, restituiscila
        if hasattr(user, 'stripe_subscription_id') and user.stripe_subscription_id:
            subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
            
            return JsonResponse({
                'subscriptionId': subscription.id,
                'clientSecret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice and subscription.latest_invoice.payment_intent else None,
            })
        
        # Se l'utente non ha un ID cliente Stripe, creane uno
        customer_id = getattr(user, 'stripe_customer_id', None)
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
            )
            
            customer_id = customer.id
            
            # Aggiorna l'utente con l'ID cliente
            user.stripe_customer_id = customer_id
            user.save()

        # Ottieni il piano di prezzo in base al ruolo o al tipo di piano richiesto
        price_lookup = price_id
        # Se non viene fornito un ID prezzo specifico, usa il tipo di piano per determinare il prezzo
        if not price_lookup and plan_type:
            # Qui potremmo avere una logica per determinare il prezzo in base al tipo di piano
            # Per ora, usiamo un valore predefinito dalle impostazioni
            price_lookup = getattr(settings, 'STRIPE_PRICE_ID', None)
        
        if not price_lookup:
            return JsonResponse({'error': 'Price ID is required'}, status=400)

        # Crea la sottoscrizione
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_lookup}],
            payment_behavior='default_incomplete',
            payment_settings={'payment_method_types': ['card'], 'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )

        # Aggiorna l'utente con l'ID della sottoscrizione
        user.stripe_subscription_id = subscription.id
        user.save()

        # Restituisci i dati della sottoscrizione
        return JsonResponse({
            'subscriptionId': subscription.id,
            'clientSecret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice and subscription.latest_invoice.payment_intent else None,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_crypto_payment(request):
    """
    Crea un pagamento in criptovaluta
    """
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        artwork_id = data.get('artworkId')
        crypto_currency = data.get('cryptoCurrency', 'bitcoin')

        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)

        amount_in_cents = int(float(amount) * 100)
        
        # Crea una sessione di checkout di Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': f'Artwork #{artwork_id}' if artwork_id else 'Art purchase',
                        'description': f'Payment in {crypto_currency}',
                    },
                    'unit_amount': amount_in_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{request.build_absolute_uri("/payment/success")}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.build_absolute_uri('/payment/cancel'),
            metadata={
                'artwork_id': str(artwork_id) if artwork_id else None,
                'user_id': str(request.user.id) if request.user.is_authenticated else None,
                'crypto_currency': crypto_currency,
            },
        )

        return JsonResponse({
            'sessionId': session.id,
            'url': session.url,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def check_payment_status(request, payment_id):
    """
    Verifica lo stato di un pagamento
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        return JsonResponse({
            'status': payment_intent.status,
            'amount': payment_intent.amount / 100,
            'currency': payment_intent.currency,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Gestisce i webhook di Stripe per aggiornare lo stato dell'utente
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    if not sig_header or not endpoint_secret:
        return JsonResponse({'error': 'Webhook signature or secret missing'}, status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Gestisci i vari eventi di Stripe
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        # Aggiorna lo stato di pagamento nella tua applicazione
        pass
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        # Gestisci il fallimento del pagamento
        pass
    elif event.type in ['customer.subscription.created', 'customer.subscription.updated']:
        subscription = event.data.object
        # Aggiorna lo stato della sottoscrizione dell'utente
        pass
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        # Rimuovi l'abbonamento dell'utente e aggiorna il ruolo se necessario
        pass
    elif event.type == 'invoice.payment_succeeded':
        invoice = event.data.object
        # Conferma che l'utente ha pagato l'abbonamento
        pass
    elif event.type == 'invoice.payment_failed':
        invoice = event.data.object
        # Gestisci il fallimento del pagamento dell'abbonamento
        pass

    return JsonResponse({'received': True})

def get_payment_method_types(method):
    """
    Restituisce i tipi di metodo di pagamento in base al metodo selezionato
    """
    if method == 'card':
        return ['card']
    elif method == 'sepa':
        return ['sepa_debit']
    elif method == 'ideal':
        return ['ideal']
    elif method == 'bancontact':
        return ['bancontact']
    elif method == 'sofort':
        return ['sofort']
    else:
        return ['card'] 