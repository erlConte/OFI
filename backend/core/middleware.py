from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT', 100)  # richieste per minuto
        self.window = 60  # finestra in secondi

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def __call__(self, request):
        # Salta il rate limiting per gli admin
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        ip = self.get_client_ip(request)
        key = f'rate_limit_{ip}'
        
        # Ottieni il timestamp corrente
        now = int(time.time())
        
        # Ottieni la lista dei timestamp delle richieste
        requests = cache.get(key, [])
        
        # Rimuovi i timestamp più vecchi della finestra
        requests = [ts for ts in requests if now - ts < self.window]
        
        # Se abbiamo superato il limite
        if len(requests) >= self.rate_limit:
            return HttpResponse(
                'Troppe richieste. Riprova più tardi.',
                content_type='text/plain',
                status=429
            )
        
        # Aggiungi il nuovo timestamp
        requests.append(now)
        cache.set(key, requests, self.window)
        
        return self.get_response(request) 