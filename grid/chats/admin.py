from django.contrib import admin

from .models import ChatRoom, Message


admin.site.register(ChatRoom)

admin.site.register(Message)

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ("content", "posted_by", "recipient_user", "recipient_client", "job", "read_status", "created_at")
#     list_filter = ("read_status", "posted_by", "recipient_client", "job")
#     search_fields = ("content", "posted_by__username", "recipient_user__username", "recipient_client__company_name")
#     ordering = ("-created_at",)


# @admin.register(MessageAttachment)
# class MessageAttachmentAdmin(admin.ModelAdmin):
#     list_display = ("file_name", "file_size", "file_type", "message")
#     search_fields = ("file_name", "message__content")
#     ordering = ("message",)


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ("user", "notification_type", "message", "is_read", "created_at", "conversation_id")
#     list_filter = ("notification_type", "is_read")
#     search_fields = ("user__username", "message", "conversation_id")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     def get_queryset(self, request):
#         # Customize queryset to optimize loading in admin panel if needed
#         return super().get_queryset(request).select_related("user")
