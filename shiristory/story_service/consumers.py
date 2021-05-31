import json
from datetime import datetime

from bson import ObjectId
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from shiristory.story_service.models import StoryGroup, StoryObject
from shiristory.settings import DATETIME_FORMAT


class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({'message': 'conn successful'}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'reply': message
        }))

class StoryConsumer(WebsocketConsumer):
    def connect(self):
        self.story_id = self.scope["url_route"]["kwargs"]["story_id"]

        # Join room group (channels library function)
        async_to_sync(self.channel_layer.group_add)(
            self.story_id,
            self.channel_name
        )

        self.accept()
        self.send(text_data=json.dumps({'message': f'{self.story_id} story conn successful'}))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.story_id,
            self.channel_name
        )

    # receive message from websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.story_id,
            {
                'type': 'chat_message',
                'message': text_data_json
            }
        )

    # Receive message from room group (this is an event handler)
    def chat_message(self, event):
        recv_message = event['message']

        new_story_id = ObjectId()
        new_datetime = datetime.now()
        recv_message["story_id"] = str(new_story_id)
        recv_message["datetime"] = new_datetime.strftime(DATETIME_FORMAT)

        # TODO: write to cache here


        # Send message to WebSocket
        self.send(text_data=json.dumps(recv_message))

        # TODO: write to main db here?
        current_group = StoryGroup.objects.get(_id=ObjectId(self.story_id))
        current_group.stories.append({
            '_id': new_story_id ,
            'author': recv_message['author'],
            'story_type': recv_message['story_type'],
            'story_content': recv_message['story_content'],
            'next_story_type': recv_message['next_story_type'],
            'datetime': new_datetime,
            'vote_count': 0
        })

        current_group.save()