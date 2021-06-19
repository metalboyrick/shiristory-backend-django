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

        if text_data_json["biztype"] == "chat_message":
            new_story_id = ObjectId()
            new_datetime = datetime.now()
            text_data_json["story_id"] = str(new_story_id)
            text_data_json["datetime"] = new_datetime.strftime(DATETIME_FORMAT)

            # Send message to room group (This repeats and sends to everyone in the socket room)
            async_to_sync(self.channel_layer.group_send)(
                self.story_id,
                {
                    'type': 'chat_message',
                    'message': text_data_json
                }
            )

            # write to main db
            current_group = StoryGroup.objects.get(_id=ObjectId(self.story_id))
            current_group.stories.append({
                '_id': new_story_id,
                'author': text_data_json['author'],
                'story_type': text_data_json['story_type'],
                'story_content': text_data_json['story_content'],
                'next_story_type': text_data_json['next_story_type'],
                'datetime': new_datetime,
                'vote_count': 0
            })

            current_group.save()

    # Receive message from room group (this is an event handler)
    def chat_message(self, event):
        recv_message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(recv_message))

