from rest_framework import serializers

from user.serializers.user import UserSerializer
from wishlist.models import WishLists, WishListsItems


class WishListItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishListsItems
        fields = ['id', 'text']


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishLists
        fields = '__all__'
    id = serializers.IntegerField()
    title = serializers.CharField()
    text = serializers.CharField(required=False,)
    share_users = UserSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    items = serializers.SerializerMethodField()

    def get_items(self, wishlist):
        items = WishListsItems.objects.filter(wishlist_id=wishlist.id).all()
        serializer = WishListItemsSerializer(items, many=True)
        return serializer.data


class WishListNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishLists
        fields = '__all__'
    title = serializers.CharField()
    text = serializers.CharField(required=False)
    share_users = UserSerializer(many=True, read_only=True)
    author_id = serializers.IntegerField()
    items = serializers.ListField(required=False)

    def create(self, validated_data):
        title = validated_data.get('title')
        text = validated_data.get('text')
        author_id = validated_data.get('author_id')
        wishlist = WishLists.objects.create(title=title, text=text, author_id=author_id)

        return wishlist


class WishListEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishLists
        fields = '__all__'

    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    share_users = UserSerializer(many=True, read_only=True)
    author_id = serializers.IntegerField(read_only=True)


