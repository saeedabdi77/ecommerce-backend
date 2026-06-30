from django.urls import path

from installation.views import InstallationDeviceTypeListView, GameListView

urlpatterns = [
    path("devices/", InstallationDeviceTypeListView.as_view()),
    path("games/", GameListView.as_view()),
]
