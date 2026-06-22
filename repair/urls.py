from django.urls import path

from repair.views import DeviceView, ProblemTypesView

urlpatterns = [
    path("devices/", DeviceView.as_view()),
    path("problem-types/", ProblemTypesView.as_view()),
]
