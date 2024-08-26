import logging
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token

# Configurar el logger
logger = logging.getLogger(__name__)

PROTECTED_URL = '/game/api/players/'

class AuthTokenTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "test"
        self.password = "test123"
        self.email = "test@email.com"
        self.user = User.objects.create_user(username=self.username,
                                        password=self.password,
                                        email=self.email)

    def test_auth_user(self):

        response = self.client.post('/api-token-auth/', {
            "username": self.username,
            "password": self.password
        })

        # Verifica que la respuesta es 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        # Comprobar que devuelve un token
        self.assertContains(response, 'token')


    def test_user_not_exist(self):

        # Usuario no existe
        response = self.client.post('/api-token-auth/', {
            "username": "bad_user",
            "password": self.password
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_password_not_auth(self):

        # Usuario no existe
        response = self.client.post('/api-token-auth/', {
            "username": self.username,
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_token_authentication(self):
        # Intentar autenticar con un token inválido
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken123')
        response = self.client.get(PROTECTED_URL)
        
        # Verificar que la autenticación falle
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_missing_token_authentication(self):
        # Intentar acceder sin un token
        response = self.client.get(PROTECTED_URL)
        
        # Verificar que la autenticación falle
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)