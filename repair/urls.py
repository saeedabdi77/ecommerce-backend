from django.urls import path

from repair.views import DeviceView

urlpatterns = [
    path("problem-types/", DeviceView.as_view()),
]
