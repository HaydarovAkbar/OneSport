from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django_filters.rest_framework import DjangoFilterBackend

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

from .models import (
    ChatRoom, 
    Message
)

from .serializers import (
    ChatRoomSerializer, 
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
)

from .filters import (
    ChatRoomFilter, 
    MessageFilter,
)

async def notify_participants(message, event_type):
    """
    Notify participants in a chat room about an event.
    """
    channel_layer = get_channel_layer()

    if channel_layer:

        await channel_layer.group_send(
            f"chat_{str(message['chat_room'])}",
            {
                "type": event_type,
                "message": message, 
            }
        )


class ChatRoomListView(generics.ListAPIView):
    """
    Handles listing chat rooms.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class=ChatRoomFilter
    permission_classes = [permissions.IsAuthenticated]

class ChatRoomCreateView(generics.CreateAPIView):
    """
    Handles reating chat rooms.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a chat room.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field='uuid'


class MessageCreateView(generics.CreateAPIView):
    """
    Handles creating messages in a chat room.
    """
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Save the message and set sender to the authenticated user
        message_created = serializer.save(sender=self.request.user)

        # Prepare the notification payload
        message = {
            "uuid": str(message_created.uuid),
            "sender": str(message_created.sender.uuid),
            "chat_room": str(message_created.chat_room.uuid),
            "file": message_created.file.url if message_created.file else None,
            "job": str(message_created.job.uuid) if message_created.job else None,
            "content": message_created.content if message_created.content else None,
            "timestamp": message_created.timestamp.isoformat(),
            "is_edited": message_created.is_edited,
            "is_viewed": message_created.is_viewed,
            "read_by": list(message_created.read_by.values_list('uuid', flat=True)),  # Serialize read_by as a list
        }

        async_to_sync(notify_participants)(message, "message_created")


class MessageListView(generics.ListAPIView):
    """
    Handles listing  messages in a chat room.
    """
    queryset=Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class=MessageFilter
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Fetch the queryset filtered by the chat room
        queryset = self.filter_queryset(self.get_queryset())

        # Update the `is_viewed` field for all messages in the queryset
        # and add the current user to the `read_by` field
        for message in queryset:
            # Mark the message as viewed
            message.is_viewed = True
            # Add the current user to the read_by field (only if not already in the list)
            message.read_by.add(self.request.user)
            message.save()

        # Serialize the updated queryset
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)
    
class MessageDetailView(generics.RetrieveUpdateAPIView):
    """
    Handles retrieving, updating, and deleting messages.
    """
    queryset=Message.objects.all()
    serializer_class = MessageUpdateSerializer
    lookup_field='uuid'
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        message_updated = self.get_object()
        message_updated.is_edited = True
        serializer = self.get_serializer(message_updated, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = {
            "uuid": str(message_updated.uuid),
            "sender": str(message_updated.sender.uuid), 
            "chat_room": str(message_updated.chat_room.uuid),
            "file": message_updated.file.url if message_updated.file else None,
            "content": message_updated.content if message_updated.content else None, 
            "job": str(message_created.job.uuid) if message_updated.job else None,  
            "timestamp": message_updated.timestamp.isoformat(),
            "is_edited": message_updated.is_edited,
            "is_viewed": message_updated.is_viewed,
            "read_by": [str(uuid) for uuid in message_updated.read_by.values_list("uuid", flat=True)],
        }
        async_to_sync(notify_participants)(message, "message_updated")
        return Response(serializer.data)

class MessageDestroyView(generics.DestroyAPIView):
    """
    Handles retrieving, updating, and deleting messages.
    """
    queryset=Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field='uuid'
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        message_deleted= self.get_object()
        if self.request.user.uuid != message_deleted.sender.uuid:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        message = {
            "uuid": str(message_deleted.uuid),
            "sender": str(message_deleted.sender.uuid), 
            "chat_room": str(message_deleted.chat_room.uuid),
            "file": message_deleted.file.url if message_deleted.file else None,
            "content": message_deleted.content if message_deleted.content else None, 
            "job": str(message_deleted.job.uuid) if message_deleted.job else None,  
            "timestamp": message_deleted.timestamp.isoformat(),
            "is_edited": message_deleted.is_edited,
            "is_viewed": message_deleted.is_viewed,
            "read_by": [str(uuid) for uuid in message_deleted.read_by.values_list("uuid", flat=True)],
        }
        async_to_sync(notify_participants)(message, "message_deleted")

        if message_deleted.delete():
            async_to_sync(notify_participants)(message, "message_deleted")
        return Response({"detail": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



