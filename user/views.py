import json
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from starProject.exceptions import WrongHashException
from starProject.http import JSONResponse
from starProject.utils import log_debug, generate_token
from .models import Users


class Registration(APIView):

    isLogin = None

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data
        password1 = data.get('password1')
        password2 = data.get('password2')
        username = data.get('username')
        email = data.get('email', '')
        context = {}
        if not username:
            return JSONResponse({'error': 'username exist'}, status=HTTP_200_OK)
        if password1 == password2:
            data_create = {'username': username, 'password': password1, 'email': email}
            user, created = Users.objects.get_or_create(username=username, defaults=data_create)
            if created:
                token = generate_token(user)
                context['message'] = 'user created'
                context['token'] = token
            else:
                context['error'] = 'user with this username already exist'
        else:
            context['error'] = 'password don\'t match'
        return JSONResponse(context, status=HTTP_200_OK)


class Login(APIView):

    isLogin = None

    def get(self, request):
        data = request.GET
        auth = data.get('auth', '{}')
        auth = json.loads(auth)
        username = auth.get('username')
        password = auth.get('password')
        if auth:
            try:
                user = Users.objects \
                    .only('username', 'password') \
                    .get(username=username)
                _hash = user.password
                if _hash != password:
                    # Авторизация не прошла
                    raise WrongHashException
            except Users.DoesNotExist:
                return JSONResponse({'error': {'auth': True}}, status=HTTP_401_UNAUTHORIZED)
            except WrongHashException:
                return JSONResponse({'error': {'auth': True}}, status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                log_debug(e)
                return JSONResponse({'error': {'authexception': True}}, status=HTTP_401_UNAUTHORIZED)

            # Генерим токен
            token = generate_token(user)
            response = {
                'auth': True,
                # Получили токен типа byte (python 3+). Конвертим в строку
                'token': token.decode('utf-8')
            }
            return JSONResponse(response, status=HTTP_200_OK)

        return JSONResponse({'error': {'auth': True}}, status=HTTP_401_UNAUTHORIZED)


class Logout(APIView):

    def post(self, request, *args, **kwargs):
        # clear cech in browser
        context = {
            'message': 'logout'
        }
        return JSONResponse(context, status=HTTP_200_OK)
