from django.urls import path

from installation.views import InstallationDeviceTypeListView, GameListView, DraftInstallationRequestRetrieveView, \
    InstallationRequestItemViewSet

from rest_framework import routers

urlpatterns = [
    path("devices/", InstallationDeviceTypeListView.as_view()),
    path("games/", GameListView.as_view()),
    path("requests/draft/", DraftInstallationRequestRetrieveView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'requests/items', InstallationRequestItemViewSet, basename='address')
urlpatterns += router.urls
