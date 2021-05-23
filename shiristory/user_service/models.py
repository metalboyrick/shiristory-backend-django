from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    profile_pic_url = models.CharField(max_length=200, null=True)
    nickname = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    # TODO friends, chats, posts list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

