"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

# Importa i consumer WebSocket
from live_streams.consumers import LiveStreamConsumer
from auctions.consumers import AuctionConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Inizializza l'applicazione ASGI di Django
django_asgi_app = get_asgi_application()

# Definisci i pattern di routing WebSocket
websocket_urlpatterns = [
    re_path(r'ws/live/(?P<stream_id>[^/]+)/$', LiveStreamConsumer.as_asgi()),
    re_path(r'ws/auction/(?P<auction_id>[^/]+)/$', AuctionConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
