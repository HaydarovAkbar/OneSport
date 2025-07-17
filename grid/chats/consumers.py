import json

from urllib.parse import parse_qs

import jwt

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Parse query string
        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        # Validate token
        if token:
            try:
                validated_token = await sync_to_async(JWTAuthentication().get_validated_token)(token)
                user = await sync_to_async(JWTAuthentication().get_user)(validated_token)
                self.scope["user"] = user
            except InvalidToken:
                self.scope["user"] = AnonymousUser()

        # Accept connection if authenticated
        if bool(self.scope["user"] and self.scope["user"].is_authenticated):
            await self.accept()
        else:
            await self.close(code=4001)  # Unauthorized
            return  # Ensure no further processing

        # Initialize the set to track typing users
        self.typing_users = set()

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Remove the user from typing users on disconnect
        user = self.scope["user"].uuid
        self.typing_users.discard(user)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def get_chat_room(self):
        from .models import ChatRoom

        return await sync_to_async(ChatRoom.objects.get)(uuid=self.room_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "typing":
            # Handle typing indicator
            typing = data.get("typing", False)
            user = self.scope["user"]

            if user.is_authenticated:
                user_uuid = str(user.uuid)

                if typing:
                    # Add user to typing users
                    self.typing_users.add(user_uuid)
                else:
                    # Remove user from typing users
                    self.typing_users.discard(user_uuid)

                # Broadcast typing notification to all users
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_notification",
                        "typing_users": list(self.typing_users),  # Convert set to list
                    },
                )
            else:
                # Optionally, send an error message if the user is not authenticated
                await self.send(text_data=json.dumps({"error": "Unauthorized"}))

        elif event_type == "message_read":
            from .models import Message

            message_id = data.get("message_id")
            user = self.scope["user"]

            # Update the message read status
            message = await sync_to_async(Message.objects.get)(uuid=message_id)

            # Add the user to the read_by field
            await sync_to_async(message.read_by.add)(user)

            # Save the message if necessary (not usually needed after a ManyToMany field update)
            await sync_to_async(message.save)()

            # Notify other users in the room that the message has been read
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_read_notification",
                    "message_id": str(message_id),
                    "user_id": str(user.uuid),
                },
            )

    async def message_created(self, event):
        await self.send(text_data=json.dumps({"type": "message_created", "message": event["message"]}))
        # print(event)

    async def message_updated(self, event):
        await self.send(text_data=json.dumps({"type": "message_updated", "message": event["message"]}))
        # print(event)

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({"type": "message_deleted", "message": event["message"]}))
        # print(event)

    async def typing_notification(self, event):
        # Send typing notification to all WebSocket connections
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "typing_users": event["typing_users"],  # List of users who are typing
                }
            )
        )

    async def message_read_notification(self, event):
        message_id = event["message_id"]
        user_id = event["user_id"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "message_read",
                    "message_id": message_id,
                    "user_id": user_id,
                }
            )
        )

    # @database_sync_to_async
    # def get_messages(self):
    #     from .models import Message
    #     return Message.objects.all()

    # async def send_message_list(self):

    #     from .serializers import MessageSerializer

    #     # Get chat room instance
    #     chat_room_instance = await self.get_chat_room()
    #     # Fetch messages asynchronously
    #     messages = await self.get_messages()

    #     # Serialize messages
    #     message_list = [MessageSerializer(message).data for message in messages]

    #     # Send the list to the WebSocket
    #     await self.send(text_data=json.dumps({
    #         "type": "message_list",
    #         "messages": message_list,
    #     }))

    # async def create_message(self, data):
    #     from .models import Message
    #     from .serializers import MessageSerializer

    #     # Call the get_chat_room method and await its result
    #     chat_room_instance = await self.get_chat_room()
    #     user_instance= await self.get_user()
    #     message = await sync_to_async(Message.objects.create)(
    #         sender=self.scope["user"],
    #         chat_room=chat_room_instance,
    #         content=data["content"],
    #         file=data.get("file", None)
    #     )
    #     return MessageSerializer(message).data
    # async def connect(self):
    #     self.room_id = self.scope['url_route']['kwargs']['room_id']
    #     self.room_group_name = f"chat_{self.room_id}"

    #     # Initialize the set to track typing users
    #     self.typing_users = set()

    #     # Join room group
    #     await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    #     await self.accept()

    # Optionally send an initial message list
    # await self.send_message_list()
