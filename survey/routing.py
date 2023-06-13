from django.urls import path
from .consumers import WSConsumer, WSConsumerAsync

ws_urlpatterns = [
    path("ws/some_url/", WSConsumerAsync.as_asgi()),
]
