from djongo import models
from django.contrib.auth.models import AbstractUser

from shiristory import settings


class User(AbstractUser):
    # Inherited fields
    # password, username, first_name, last_name, email,
    # is_superuser, is_staff, is_active, last_login, date_joined

    _id = models.ObjectIdField()
    profile_pic_url = models.CharField(max_length=200, null=True)
    nickname = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    friends = models.ArrayReferenceField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # TODO chats, posts list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
