from django.urls import path
from rest_framework import routers

from order.views import CartRetrieveView, CartItemViewSet, SelectDeliveryAddressView

urlpatterns = [
    path("cart/", CartRetrieveView.as_view()),
    path("delivery-address/", SelectDeliveryAddressView.as_view(), name="order-delivery-address"),
]

router = routers.DefaultRouter()
router.register(r'cart/items', CartItemViewSet, basename='cart-item')
urlpatterns += router.urls
