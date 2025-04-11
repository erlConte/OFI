"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.documentation import include_docs_urls

def api_root(request):
    return JsonResponse({
        "message": "Benvenuto nell'API di OFI",
        "documentation": "/api/docs/",
        "endpoints": {
            "users": "/api/users/",
            "artworks": "/api/artworks/",
            "live-streams": "/api/live-streams/",
            "auctions": "/api/auctions/",
            "events": "/api/events/",
            "qr": "/api/qr/",
            "media": "/api/media/",
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/artworks/', include('artworks.urls')),
    path('api/live-streams/', include('live_streams.urls')),
    path('api/auctions/', include('auctions.urls')),
    path('api/events/', include('events.urls')),
    path('api/qr/', include('qr_system.urls')),
    path('api/media/', include('media.urls')),
    path('api/payment/', include('payment.urls')),
    path('api/docs/', include_docs_urls(title='OFI API')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
