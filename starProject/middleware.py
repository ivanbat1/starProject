from datetime import datetime

import jwt

from user.models import Users
from rest_framework import status

from .http import JSONResponse
from .settings import SECRET_KEY


class User():
    user_id = None
    whois = None

    def get_user(self):
        return Users.objects.get(id=self.user_id)

    def get_user_id(self):
        return self.user_id

    def get_whois(self):
        return self.whois

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_whois(self, whois):
        self.whois = whois


class RequestInterceptor(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        initkwargs = getattr(view_func, 'view_initkwargs', None)
        if initkwargs != None:
            # По умолчанию для всех url нужна авторизация
            isLogin = initkwargs.get('isLogin', True)
            if isLogin:
                auth = request.META.get('HTTP_AUTHORIZATION')
                response_error = {
                    'auth': False,
                    'errors': 'Потрібно авторизуватись!'
                }
                # Выдергиваем токен с заголовка запроса
                if auth and auth.startswith('Bearer JWT '):
                    token = auth[11:]
                    try:
                        body = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                        if datetime.fromtimestamp(body.get('exp')) < datetime.now():
                            return JSONResponse(response_error,
                                                status=status.HTTP_401_UNAUTHORIZED)
                        user_id = body.get('user_id')
                        # transfer user_id in to view
                        request.user_id = user_id

                        # save user_id
                        user = User()
                        try:
                            ip = request.META['HTTP_X_REAL_IP']
                        except:
                            ip = request.META['REMOTE_ADDR']
                        app_name = 'starProject'
                        whois = '%s:%s:%s' % (app_name, user_id, ip)
                        user.set_user_id(user_id)
                        user.set_whois(whois)

                    except Exception as e:
                        print(e)
                        return JSONResponse(response_error,
                                            status=status.HTTP_401_UNAUTHORIZED)

                else:
                    return JSONResponse(response_error,
                                        status=status.HTTP_401_UNAUTHORIZED)