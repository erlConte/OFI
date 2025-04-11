from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Credenziali non valide'
        }, status=401)

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'error': 'Username già in uso'
        }, status=400)
        
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'success': False,
            'error': 'Email già in uso'
        }, status=400)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }) 