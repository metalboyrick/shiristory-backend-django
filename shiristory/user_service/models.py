from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_pic_url = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.username
