from django.urls import path
from .views import ProfileViewSet

from rest_framework import routers

urlpatterns = [
    path("profile/", ProfileViewSet.as_view({'get': 'retrieve', 'post': 'create', 'put': 'update'})),
]



router = routers.DefaultRouter()
# router.register(r'profile', ProfileViewSet, basename='profile')
urlpatterns += router.urls