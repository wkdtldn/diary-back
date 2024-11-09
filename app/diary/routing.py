# routing.py
from django.urls import path
from . import consumers  # WebSocket 소비자 모듈

websocket_urlpatterns = [
    path("ws/activity/", consumers.ActivityConsumer.as_asgi()),  # WebSocket 경로
]
