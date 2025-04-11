import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Auction
from django.utils import timezone

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'auction_{self.auction_id}'

        # Verifica che l'asta esista e sia attiva
        if await self.is_valid_auction():
            # Unisciti al gruppo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Invia stato iniziale
            await self.send_auction_status()
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
        
        if message_type == 'place_bid':
            # Gestisci una nuova offerta
            amount = text_data_json.get('amount')
            user_id = text_data_json.get('user_id')
            success, message = await self.place_bid(user_id, amount)
            
            await self.send(text_data=json.dumps({
                'type': 'bid_response',
                'success': success,
                'message': message
            }))
            
            if success:
                # Invia aggiornamento a tutti i client
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'auction_update',
                        'current_price': amount,
                        'highest_bidder': user_id,
                        'time_remaining': await self.get_time_remaining()
                    }
                )

    async def auction_update(self, event):
        # Invia aggiornamenti dell'asta
        await self.send(text_data=json.dumps({
            'type': 'auction_update',
            'current_price': event['current_price'],
            'highest_bidder': event['highest_bidder'],
            'time_remaining': event['time_remaining']
        }))

    @database_sync_to_async
    def is_valid_auction(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            return auction.is_active
        except Auction.DoesNotExist:
            return False

    @database_sync_to_async
    def place_bid(self, user_id, amount):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            success, message = auction.place_bid(user_id, amount)
            return success, message
        except Auction.DoesNotExist:
            return False, "Asta non trovata"

    @database_sync_to_async
    def get_auction_status(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            return {
                'current_price': auction.current_price,
                'highest_bidder': auction.highest_bidder.id if auction.highest_bidder else None,
                'total_bids': auction.total_bids,
                'unique_bidders': auction.unique_bidders,
                'time_remaining': auction.time_remaining.total_seconds() if auction.time_remaining else None
            }
        except Auction.DoesNotExist:
            return None

    @database_sync_to_async
    def get_time_remaining(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            if auction.time_remaining:
                return auction.time_remaining.total_seconds()
            return None
        except Auction.DoesNotExist:
            return None

    async def send_auction_status(self):
        status = await self.get_auction_status()
        if status:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'auction_update',
                    'current_price': status['current_price'],
                    'highest_bidder': status['highest_bidder'],
                    'time_remaining': status['time_remaining']
                }
            ) 