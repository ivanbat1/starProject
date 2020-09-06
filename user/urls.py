from django.urls import path
from .views import Registration, Login, Logout

urlpatterns = [
    path('registration/', Registration.as_view(isLogin=False)),
    path('login/', Login.as_view(isLogin=False)),
    path('logout/', Logout.as_view()),
]
