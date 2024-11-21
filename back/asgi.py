"""
ASGI config for back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from diary import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.settings")

application = get_asgi_application()

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),  # HTTP 요청을 처리
#         "websocket": AuthMiddlewareStack(  # WebSocket 요청을 처리
#             URLRouter(routing.websocket_urlpatterns)  # WebSocket 라우팅 설정
#         ),
#     }
# )