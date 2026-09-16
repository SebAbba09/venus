# Venus_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Venus.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Venus_project.settings')

# Initialise l'application Django
django_asgi_app = get_asgi_application()

# Définir l'application ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Configure les WebSockets
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
