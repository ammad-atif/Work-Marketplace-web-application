from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import *
import json
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user=self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat=get_object_or_404(Chat, id=self.chat_id)

        async_to_sync(self.channel_layer.group_add)(
            self.chat_id,self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id,self.channel_name
        )
    def receive(self,text_data):
        text_data_json = json.loads(text_data)
        body=text_data_json['body']
        message=Message.objects.create(chat=self.chat,author=self.user,body=body)
        event = {
            'type':'message_handler',
            'message_id':message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chat_id,event 
        )
    def message_handler(self,event):
        message_id=event['message_id']
        message=Message.objects.get(id=message_id)
        content={"message":message,"user":self.user}
        html=render_to_string("chat/message.html", content)
        self.send(text_data=html)
