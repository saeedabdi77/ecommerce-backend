from django.urls import path
from rest_framework import routers

from repair.views import DevicesListView, ProblemTypesListView, RepairRequestViewSet

urlpatterns = [
    path("devices/", DevicesListView.as_view()),
    path("problem-types/", ProblemTypesListView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'requests', RepairRequestViewSet, basename='address')
urlpatterns += router.urls
