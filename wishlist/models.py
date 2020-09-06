from django.db import models
from user.models import Users


class WishLists(models.Model):
    class Meta:
        db_table = 'wishlists'
    title = models.CharField(
        null=False,
        blank=True,
        max_length=255)
    text = models.TextField()
    share_users = models.ManyToManyField(
        Users,
        related_name='share_users')
    author = models.ForeignKey(
        Users,
        related_name='author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    date_create = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        auto_now=False)
    date_update = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=False,
        auto_now=True)


class WishListsItems(models.Model):
    class Meta:
        db_table = 'wishlists_items'
    text = models.TextField()
    date_create = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        auto_now=False)
    date_update = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=False,
        auto_now=True)
    wishlist = models.ForeignKey(
        WishLists,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

