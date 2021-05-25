import datetime

from django import forms
from djongo import models

from shiristory.base.abstract_base_model import AbstractBaseModel
from shiristory.user_service.models import User


class StoryObject(AbstractBaseModel):
    # Choices for story type
    class StoryType(models.IntegerChoices):
        TEXT = 0
        IMAGE = 1
        AUDIO = 2
        VIDEO = 3

    _id = models.ObjectIdField()
    author = models.CharField(max_length=255)
    story_type = models.IntegerField(choices=StoryType.choices, blank=False)
    story_content = models.CharField(max_length=255, blank=False)
    next_story_type = models.IntegerField(choices=StoryType.choices, blank=False)
    datetime = models.DateTimeField(default=datetime.datetime.now())
    vote_count = models.IntegerField(default=0, blank=False)

    def get_id(self):
        return str(self.pk)

    class Meta:
        abstract = True


class StoryObjectForm(forms.ModelForm):
    class Meta:
        model = StoryObject
        fields = (
            'author', 'story_type', 'story_content', 'next_story_type', 'vote_count'
        )


class VotePool(AbstractBaseModel):
    vote_end_time = models.DateTimeField()

    candidates = models.ArrayField(
        model_container=StoryObject,
        model_form_class=StoryObjectForm,
        blank=True
    )

    class Meta:
        abstract = True

    def get_id(self):
        return str(self.pk)

class StoryGroup(AbstractBaseModel):
    # choices for story status
    class StoryStatus(models.IntegerChoices):
        ONGOING = 0
        FINISHED = 1

    _id = models.ObjectIdField()
    group_name = models.CharField(max_length=255, blank=False)
    group_members = models.ArrayReferenceField(
        to=User,
        on_delete=models.CASCADE,
        related_name='group_members'
    )

    group_admins = models.ArrayReferenceField(
        to=User,
        on_delete=models.CASCADE,
        related_name='group_admins'
    )

    date_created = models.DateTimeField(default=datetime.datetime.now())
    last_modified = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=StoryStatus.choices, blank=False)
    vote_duration = models.DurationField()
    vote_threshold = models.IntegerField()

    stories = models.ArrayField(
        model_container=StoryObject,
        model_form_class=StoryObjectForm,
        blank=True
    )

    vote_pool = models.EmbeddedField(
        model_container=VotePool
    )

    def get_id(self):
        return str(self.pk)
