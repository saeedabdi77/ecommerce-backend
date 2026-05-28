from django.urls import path
from .views import ProfileViewSet, AddressViewSet

from rest_framework import routers

urlpatterns = [
    path("profile/", ProfileViewSet.as_view({'get': 'retrieve', 'post': 'create', 'put': 'update'})),
]

router = routers.DefaultRouter()
router.register(r'address', AddressViewSet, basename='address')
urlpatterns += router.urls