from django.urls import path

from .views import GameView, WinView, LoseView, DrawView

urlpatterns = [
    path("", GameView.as_view(), name="game"),
    path("win/", WinView.as_view(), name="win"),
    path("lose/", LoseView.as_view(), name="lose"),
    path("draw/", DrawView.as_view(), name="draw"),
]