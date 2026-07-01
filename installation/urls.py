from django.urls import path

from installation.views import InstallationDeviceTypeListView, GameListView, DraftInstallationRequestRetrieveView

urlpatterns = [
    path("devices/", InstallationDeviceTypeListView.as_view()),
    path("games/", GameListView.as_view()),
    path("requests/draft/", DraftInstallationRequestRetrieveView.as_view()),
]
