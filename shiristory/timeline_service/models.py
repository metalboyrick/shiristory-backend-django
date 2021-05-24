from djongo import models

from shiristory.base.abstract_base_model import AbstractBaseModel


class Comment(AbstractBaseModel):
    # TODO: Integrate with user
    author = models.CharField(max_length=255)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField()

    objects = models.DjongoManager()

    def __str__(self):
        return self.comment

    class Meta:
        abstract = True


class Post(AbstractBaseModel):
    _id = models.ObjectIdField()
    # TODO: Integrate with user
    author = models.CharField(max_length=255)
    content = models.CharField(max_length=500)
    inv_link = models.URLField()
    media = models.URLField()
    media_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    # likes = models.ArrayReferenceField()
    comments = models.ArrayField(model_container=Comment)

    objects = models.DjongoManager()

    def get_id(self):
        return str(self.pk)
