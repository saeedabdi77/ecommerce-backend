from django.urls import path

from repair.views import DeviceView

urlpatterns = [
    path("devices/", DeviceView.as_view()),
]
