from django.urls import path

from installation.views import InstallationDeviceTypeListView

urlpatterns = [
    path("devices/", InstallationDeviceTypeListView.as_view()),
]
