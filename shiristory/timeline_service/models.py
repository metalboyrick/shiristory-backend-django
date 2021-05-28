from djongo import models

from shiristory.base.abstract_base_model import AbstractBaseModel
from shiristory.user_service.models import User


class SimpleUser(AbstractBaseModel):
    _id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    profile_pic_url = models.CharField(max_length=200, null=True)
    nickname = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.username

    class Meta:
        abstract = True


class Comment(AbstractBaseModel):
    author = models.EmbeddedField(model_container=SimpleUser)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField()

    objects = models.DjongoManager()

    def __str__(self):
        return self.comment

    class Meta:
        abstract = True


class Post(AbstractBaseModel):
    _id = models.ObjectIdField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=500)
    inv_link = models.URLField(null=True)
    media = models.URLField(null=True)
    media_type = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    likes = models.ArrayReferenceField(to=User, on_delete=models.SET_DEFAULT, related_name='likes', default=[])
    comments = models.ArrayField(model_container=Comment, default=[])

    objects = models.DjongoManager()
