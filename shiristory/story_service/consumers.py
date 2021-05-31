import json

from bson import ObjectId
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

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

    # Receive message from room group
    def chat_message(self, event):
        recv_message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(recv_message))
