from django.db import models


class Users(models.Model):
    class Meta:
        db_table = 'users'

    username = models.CharField(null=False, blank=True, max_length=255, unique=True)
    email = models.CharField(null=True, blank=True, max_length=255)
    password = models.CharField(null=True, blank=True, max_length=255)
    date_joined = models.DateTimeField(null=True, blank=True, auto_now_add=True, auto_now=False)
