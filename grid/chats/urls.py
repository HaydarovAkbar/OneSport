from django.urls import include, path

from .views import (
    ChatRoomCreateView,
    ChatRoomDetailView,
    ChatRoomListView,
    MessageCreateView,
    MessageDestroyView,
    MessageDetailView,
    MessageListView,
)


urlpatterns = [
    path("chat-room/create/", ChatRoomCreateView.as_view(), name="chat-room-create"),
    path("chat-room/list/", ChatRoomListView.as_view(), name="chat-room-list"),
    path("chat-room/<uuid:uuid>/", ChatRoomDetailView.as_view(), name="chat-room-detail"),
    path("messages/list/", MessageListView.as_view(), name="message-list"),
    path("messages/create/", MessageCreateView.as_view(), name="message-create"),
    path("messages/detail/<uuid:uuid>/", MessageDetailView.as_view(), name="message-detail"),
    path("messages/delete/<uuid:uuid>/", MessageDestroyView.as_view(), name="message-detail"),
]


# path("", include(router.urls)),
# # Custom actions
# path(
#     "notifications/delete_all_read/",
#     NotificationViewSet.as_view({"delete": "delete_all_read"}),
#     name="delete_all_read_notifications",
# ),
# path(
#     "notifications/delete_all/",
#     NotificationViewSet.as_view({"delete": "delete_all"}),
#     name="delete_all_notifications",
# ),
# path(
#     "notifications/<int:pk>/delete/", NotificationViewSet.as_view({"delete": "delete"}), name="delete_notification"
# ),
# path(
#     "notifications/<int:pk>/mark_as_read/",
#     NotificationViewSet.as_view({"post": "mark_as_read"}),
#     name="mark_notification_as_read",
# ),
# path(
#     "notifications/<int:pk>/mark_as_unread/",
#     NotificationViewSet.as_view({"post": "mark_as_unread"}),
#     name="mark_notification_as_unread",
# ),
# path(
#     "notifications/mark_all_as_read/",
#     NotificationViewSet.as_view({"post": "mark_all_as_read"}),
#     name="mark_all_notifications_as_read",
# ),
# path(
#     "notifications/mark_all_as_unread/",
#     NotificationViewSet.as_view({"post": "mark_all_as_unread"}),
#     name="mark_all_notifications_as_unread",
# ),
