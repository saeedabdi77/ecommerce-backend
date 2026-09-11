from django.urls import path
from rest_framework import routers

from order.views import CartRetrieveView, CartItemViewSet, SelectDeliveryAddressView, DeliveryMethodListView

urlpatterns = [
    path("cart/", CartRetrieveView.as_view()),
    path("delivery-address/", SelectDeliveryAddressView.as_view(), name="order-delivery-address"),
    path("delivery-methods/", DeliveryMethodListView.as_view(), name="delivery-method-list"),
]

router = routers.DefaultRouter()
router.register(r'cart/items', CartItemViewSet, basename='cart-item')
urlpatterns += router.urls
