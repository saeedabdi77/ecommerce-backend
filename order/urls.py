from django.urls import path
from rest_framework import routers

from order.views import CartRetrieveView, CartItemViewSet

urlpatterns = [
    path("cart/", CartRetrieveView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'cart/items', CartItemViewSet, basename='cart-item')
urlpatterns += router.urls
