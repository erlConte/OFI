from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        with transaction.atomic():
            # Estrai i dati dalla richiesta
            name = request.data.get('name')
            email = request.data.get('email')
            password = request.data.get('password')

            # Validazione base
            if not all([name, email, password]):
                return Response(
                    {'error': 'Tutti i campi sono obbligatori'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verifica se l'email è già in uso
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email già in uso'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crea l'utente
            user = User.objects.create_user(
                username=email,  # Usiamo l'email come username
                email=email,
                password=password,
                first_name=name.split()[0],
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                role=User.Role.BASE  # Ruolo predefinito
            )

            # Genera il token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)

            # Prepara la risposta
            response_data = {
                'token': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'email': user.email,
                    'role': user.role
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
