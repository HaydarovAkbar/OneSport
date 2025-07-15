from rest_framework import serializers
from .models import ChatRoom, Message
from ..users.models import User


class ChatRoomSerializer(serializers.ModelSerializer):
    unread_messages_count = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = ['uuid', 'recruiter', 'clients', 'unread_messages_count']
        read_only_fields=['unread_messages_count']
    

    def get_unread_messages_count(self, obj):
        user = self.context['request'].user
        # Count messages in this chat room that are not viewed by the user
        unread_count = Message.objects.filter(chat_room=obj, is_viewed=False).exclude(read_by=user).count()
        return unread_count


class MessageSerializer(serializers.ModelSerializer):

    chat_room = serializers.StringRelatedField()
    read_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)


    class Meta:
        model = Message
        fields = ['uuid', 'sender', 
                  'chat_room','job',
                  'content', 'timestamp', 
                  'file', 'is_edited', 
                  'is_viewed', 'read_by']
        
class MessageUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['uuid', 'chat_room',
                'content', 'is_edited',]


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['uuid', 'sender', 'chat_room', 'job', 'content', 'file']
        read_only_fields = ['uuid', 'sender']  # Let the server set these fields

    def validate(self, attrs):
        # Ensure at least one of 'content' or 'file' is provided
        if not attrs.get('content') and not attrs.get('file'):
            raise serializers.ValidationError("Either 'content' or 'file' must be provided.")
        return attrs

