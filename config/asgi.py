import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from grid.chats.routing import websocket_urlpatterns  # Your WebSocket routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),  # Wrapping with AuthMiddlewareStack for authentication
    }
)
