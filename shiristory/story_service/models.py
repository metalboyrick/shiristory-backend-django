from djongo import models


class Blog(models.Model):
    name = models.CharField(max_length=100)
