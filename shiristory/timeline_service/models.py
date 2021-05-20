from djongo import models


class Comment(models.Model):
    # TODO: Integrate with user
    author = models.CharField(max_length=255)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    objects = models.DjongoManager()

    class Meta:
        abstract = True


class Post(models.Model):
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
