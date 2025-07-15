from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps

from ..core.models import CoreModel

User=get_user_model()


class ChatRoom(CoreModel):
    recruiter=models.ForeignKey("recruiters.Recruiter", on_delete=models.CASCADE, related_name="chat_room")
    clients=models.ManyToManyField("clients.Client",related_name="chat_room")
    
    def __str__(self):
        return str(self.uuid)


class Message(CoreModel):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(to=User ,on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_viewed=models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    job=models.ForeignKey(to="jobs.Job", on_delete=models.CASCADE, null=True, blank=True)

    def is_read_by(self, user):
        return user in self.read_by.all()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.sender} in {self.chat_room.name}"




# class Message(CoreModel):
#     content = models.TextField()
#     posted_by = models.ForeignKey("users.User", on_delete=models.RESTRICT, related_name="sent_messages")
#     recipient_user = models.ForeignKey(
#         "users.User", on_delete=models.RESTRICT, null=True, blank=True, related_name="received_messages"
#     )
#     recipient_client = models.ForeignKey(
#         "clients.Client", on_delete=models.CASCADE, null=True, blank=True, related_name="messages"
#     )
#     job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
#     read_status = models.SmallIntegerField(choices=[(0, "New"), (1, "Read")], default=0)
#     edited = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Message by {self.posted_by} on Job {self.job.title if self.job else 'General'}"

#     def get_attachments(self):
#         return self.attachments.all()


# class MessageAttachment(CoreModel):
#     message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
#     file = models.FileField(upload_to="message_attachments/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Attachment for Message {self.message.id}"

#     @property
#     def file_name(self):
#         """Returns the name of the file."""
#         return self.file.name.split("/")[-1]

#     @property
#     def file_size(self):
#         """Returns the file size in bytes."""
#         return self.file.size if self.file else 0

#     @property
#     def file_type(self):
#         """Returns the MIME type of the file, e.g., 'application/pdf'."""
#         return self.file.file.content_type if self.file else None


# class Notification(CoreModel):
#     class NotificationType(models.IntegerChoices):
#         INFORMATIONAL = 0, "Informational"
#         ACTION_REQUIRED = 1, "Action Required"
#         SYSTEM_ALERT = 2, "System Alert"
#         REMINDER = 3, "Reminder"
#         PROMOTIONAL = 4, "Promotional"

#     user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
#     message = models.TextField()
#     notification_type = models.SmallIntegerField(
#         choices=NotificationType.choices, default=NotificationType.INFORMATIONAL
#     )
#     is_read = models.BooleanField(default=False)
#     conversation_id = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         return f"Notification for {self.user} - {self.get_notification_type_display()}"

#     @classmethod
#     def create_notification(cls, user, message, notification_type=NotificationType.INFORMATIONAL, conversation_id=None):
#         """
#         Creates and saves a new notification.
#         """
#         notification = cls.objects.create(
#             user=user,
#             message=message,
#             notification_type=notification_type,
#             conversation_id=conversation_id,
#             created_at=timezone.now(),
#         )
#         return notification
