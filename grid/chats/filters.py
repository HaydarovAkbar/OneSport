import django_filters

from .models import ChatRoom, Message


class ChatRoomFilter(django_filters.FilterSet):
    recruiter = django_filters.UUIDFilter(field_name="recruiter__uuid", lookup_expr="exact")
    client = django_filters.UUIDFilter(field_name="clients__uuid", lookup_expr="exact")

    class Meta:
        model = ChatRoom
        fields = ["recruiter", "clients"]


class MessageFilter(django_filters.FilterSet):
    sender = django_filters.UUIDFilter(field_name="sender__uuid", lookup_expr="exact")
    chat_room = django_filters.UUIDFilter(field_name="chat_room", lookup_expr="exact")
    sender_email = django_filters.CharFilter(field_name="sender__email", lookup_expr="exact")

    class Meta:
        model = Message
        fields = ["sender", "chat_room", "sender_email"]
