import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import LiveStream
from django.utils import timezone

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.room_group_name = f'live_{self.stream_id}'

        # Verifica che la live esista e sia attiva
        if await self.is_valid_stream():
            # Unisciti al gruppo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Invia stato iniziale
            await self.send_stream_status()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Rimuovi dal gruppo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'viewer_count':
            # Aggiorna il conteggio spettatori
            count = text_data_json.get('count', 0)
            await self.update_viewer_count(count)
        elif message_type == 'chat_message':
            # Inoltra il messaggio della chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data_json.get('message'),
                    'username': text_data_json.get('username')
                }
            )

    async def chat_message(self, event):
        # Invia il messaggio della chat al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    async def stream_status(self, event):
        # Invia aggiornamenti dello stato della live
        await self.send(text_data=json.dumps({
            'type': 'stream_status',
            'status': event['status'],
            'viewers': event['viewers'],
            'duration': event['duration']
        }))

    @database_sync_to_async
    def is_valid_stream(self):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            return stream.is_active
        except LiveStream.DoesNotExist:
            return False

    @database_sync_to_async
    def update_viewer_count(self, count):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            stream.update_viewers(count)
            return True
        except LiveStream.DoesNotExist:
            return False

    @database_sync_to_async
    def get_stream_status(self):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            duration = None
            if stream.started_at:
                duration = (timezone.now() - stream.started_at).total_seconds()
            
            return {
                'status': stream.status,
                'viewers': stream.viewers_count,
                'duration': duration
            }
        except LiveStream.DoesNotExist:
            return None

    async def send_stream_status(self):
        status = await self.get_stream_status()
        if status:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'stream_status',
                    'status': status['status'],
                    'viewers': status['viewers'],
                    'duration': status['duration']
                }
            ) 