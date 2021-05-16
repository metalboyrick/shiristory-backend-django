from django import forms
from djongo import models


class StoryObject(models.Model):
    # Choices for story type
    class StoryType(models.IntegerChoices):
        TEXT = 0
        IMAGE = 1
        AUDIO = 2
        VIDEO = 3

    story_id = models.ObjectIdField(primary_key=True)
    user_id = models.BigIntegerField(blank=False)
    story_type = models.IntegerField(choices=StoryType.choices, blank=False)
    story_content = models.CharField(max_length=255, blank=False)
    next_story_type = models.IntegerField(choices=StoryType.choices, blank=False)
    datetime = models.DateTimeField(blank=False)
    vote_count = models.IntegerField(default=0, blank=False)


class StoryObjectForm(forms.ModelForm):
    class Meta:
        model = StoryObject
        fields = (
            'story_id', 'user_id', 'story_type', 'story_content', 'next_story_type', 'datetime', 'vote_count'
        )


class VotePool(models.Model):
    _id = models.ObjectIdField(primary_key=True)

    vote_end_time = models.DateTimeField()

    candidates = models.ArrayField(
        model_container=StoryObject,
        model_form_class=StoryObjectForm
    )


class Group(models.Model):

    @staticmethod
    def default_array():
        return []

    # choices for story status
    class StoryStatus(models.IntegerChoices):
        ONGOING = 0
        FINISHED = 1

    group_id = models.ObjectIdField(primary_key=True)
    group_name = models.CharField(max_length=255, blank=False)
    group_members = models.JSONField(default=default_array, blank=False)
    group_admins = models.JSONField(default=default_array, blank=False)
    date_created = models.DateTimeField()
    status = models.IntegerField(choices=StoryStatus.choices, blank=False)
    vote_duration = models.DurationField()
    vote_threshold = models.IntegerField()

    stories = models.ArrayField(
        model_container=StoryObject,
        model_form_class=StoryObjectForm
    )

    vote_pool = models.EmbeddedField(
        model_container=VotePool
    )
