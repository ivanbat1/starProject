from django.urls import path
from .views import WishList, ShareWish, Wish

urlpatterns = [
    path('create/', Wish.as_view()),
    path('share/<int:wishlist>/', ShareWish.as_view()),
    path('<int:wishlist>/', Wish.as_view()),
    path('', WishList.as_view()),
]
