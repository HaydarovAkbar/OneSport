import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from grid.chats.routing import websocket_urlpatterns  # Your WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),  # Wrapping with AuthMiddlewareStack for authentication
})