from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'ws/test', TestConsumer.as_asgi()),
    re_path(r'^ws/(?P<story_id>\w+)/stories$', StoryConsumer.as_asgi())
]