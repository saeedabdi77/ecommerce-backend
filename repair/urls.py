from django.urls import path

from repair.views import DevicesListView, ProblemTypesListView, RepairRequestView

urlpatterns = [
    path("devices/", DevicesListView.as_view()),
    path("problem-types/", ProblemTypesListView.as_view()),
]
