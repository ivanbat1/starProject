import json
from django.db import transaction
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from starProject.http import JSONResponse
from starProject.utils import str_errors
from user.models import Users
from wishlist.models import WishLists, WishListsItems
from wishlist.serializers.wishlist import WishListSerializer, WishListEditSerializer, \
    WishListNewSerializer
from rest_framework.status import HTTP_200_OK


class WishList(ListAPIView):
    serializer_class = WishListSerializer

    def get_queryset(self, *args, **kwargs):
        user_id = self.request.user_id
        wishlist = WishLists.objects.filter(Q(author_id=user_id)).union(
            WishLists.objects.filter(Q(share_users__in=[user_id]))
        )
        return wishlist


def create_items(items, wishlist_id):
    for item in items:
        if not item.get('text'):
            continue
        WishListsItems.objects.create(text=item.get('text'), wishlist_id=wishlist_id)


def update_items(items, wishlist_id):
    for item in items:
        if not item.get('text') or not item.get('id'):
            continue
        WishListsItems.objects.filter(id=item.get('id'), wishlist_id=wishlist_id).update(text=item.get('text'))


class Wish(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.user_id
        data = request.data
        title = data.get('title')
        text = data.get('text')
        items = json.loads(data.get('items', '[]'))
        data_create = {
            'title': title,
            'author_id': user_id,
            'text': text,
        }
        serializer = WishListNewSerializer(data=data_create)
        if serializer.is_valid():
            serializer.save()
            if items:
                wishlist_id = serializer.data.get('id')
                create_items(items, wishlist_id)
            context = {'message': serializer.data}
            return JSONResponse(context, status=HTTP_200_OK)
        else:
            errors = str_errors(serializer.errors)
            context = {'errors': errors}
            return JSONResponse(context, status=HTTP_200_OK)

    def get(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        wishlist = WishLists.objects.filter(Q(author_id=user_id, id=wishlist) |
                                            Q(share_users__in=[user_id], id=wishlist)).first()
        if not wishlist:
            return JSONResponse({'message': 'wishlist does not exist'}, status=HTTP_200_OK)
        serializer = WishListSerializer(wishlist)
        context = {'message': serializer.data}
        return JSONResponse(context, status=HTTP_200_OK)

    @transaction.atomic
    def put(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        title = request.data.get('title')
        text = request.data.get('text')
        items = json.loads(request.data.get('items', '[]'))
        context = {'message': 'wishlist does not exist'}
        try:
            wishlist = WishLists.objects.get(id=wishlist, author_id=user_id)
        except WishLists.DoesNotExist:
            return JSONResponse(context, status=HTTP_200_OK)
        if wishlist:
            data_edit = {
                'title': title,
                'text': text,
            }
            serializer = WishListEditSerializer(wishlist, data=data_edit)
            if serializer.is_valid():
                serializer.save()
                if items:
                    wishlist_id = serializer.data.get('id')
                    update_items(items, wishlist_id)
                context = {'message': WishListSerializer(wishlist).data}
                return JSONResponse(context, status=HTTP_200_OK)
            else:
                errors = str_errors(serializer.errors)
                context = {'errors': errors}
                return JSONResponse(context, status=HTTP_200_OK)
        return JSONResponse(context, status=HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        context = {'message': 'wishlist does not exist'}
        wishlist = WishLists.objects.filter(author_id=user_id, id=wishlist)
        if wishlist:
            wishlist.delete()
            context['message'] = 'wishlist delete'
            return JSONResponse(context, status=HTTP_200_OK)
        return JSONResponse(context, status=HTTP_200_OK)


class ShareWish(APIView):
    @transaction.atomic
    def post(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        data = request.query_params
        reserve = data.get('reserve')
        context = {'message': 'wish not reserved'}
        if reserve:
            try:
                wish = WishLists.objects.get(share_users__in=[user_id], id=wishlist)
                wish_items = WishListsItems.objects.filter(wishlist_id=wish.id)
                new_wish = WishLists.objects.create(
                    title=wish.title,
                    text=wish.text,
                    author_id=user_id
                )
                for item in wish_items:
                    WishListsItems.objects.create(
                        text=item.text,
                        wishlist_id=new_wish.id
                    )

            except WishLists.DoesNotExist:
                return JSONResponse({'error': 'wishlist does not exist'}, status=HTTP_200_OK)
            except json.JSONDecodeError:
                return JSONResponse({'error': 'share users list wrong format'}, status=HTTP_200_OK)
            context['message'] = 'wish reserved'
            return JSONResponse(context, status=HTTP_200_OK)
        return JSONResponse(context, status=HTTP_200_OK)

    @transaction.atomic
    def put(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        context = {'message': 'users added'}
        try:
            share_users = json.loads(request.data.get('share_users', '[]'))
            wishlist = WishLists.objects.get(author_id=user_id, id=wishlist)
            for user in share_users:
                share_user_id = Users.objects.get(id=user.get('id')).id
                if share_user_id == user_id:
                    continue
                wishlist.share_users.add(share_user_id)
        except WishLists.DoesNotExist:
            return JSONResponse({'error': 'wishlist does not exist'}, status=HTTP_200_OK)
        except json.JSONDecodeError:
            return JSONResponse({'error': 'share users list wrong format'}, status=HTTP_200_OK)
        return JSONResponse(context, status=HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, wishlist=None, *args, **kwargs):
        user_id = request.user_id
        context = {'message': 'users deleted'}
        try:
            share_users = json.loads(request.data.get('share_users', '[]'))
            wishlist = WishLists.objects.get(author_id=user_id, id=wishlist)
            for user in share_users:
                wishlist.share_users.remove(Users.objects.get(id=user.get('id')).id)
        except WishLists.DoesNotExist:
            return JSONResponse({'error': 'wishlist does not exist'}, status=HTTP_200_OK)
        except json.JSONDecodeError:
            return JSONResponse({'error': 'share users list wrong format'}, status=HTTP_200_OK)
        return JSONResponse(context, status=HTTP_200_OK)
