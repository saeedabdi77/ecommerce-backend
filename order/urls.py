from django.urls import path
from rest_framework import routers

from order.views import CartRetrieveView, CartItemViewSet, SelectDeliveryAddressView, DeliveryMethodListView, \
    SelectDeliveryMethodView, OrderConfigRetrieveView, PaymentMethodListView, SubmitOrderPaymentView, \
    ZarinpalCallbackView

urlpatterns = [
    path("config/", OrderConfigRetrieveView.as_view(), name="order-config"),
    path("cart/", CartRetrieveView.as_view()),
    path("delivery-address/", SelectDeliveryAddressView.as_view(), name="order-delivery-address"),
    path("delivery-methods/", DeliveryMethodListView.as_view(), name="delivery-method-list"),
    path("payment-methods/", PaymentMethodListView.as_view(), name="payment-method-list"),
    path("payment/", SubmitOrderPaymentView.as_view(), name="order-payment"),
    path("payments/zarinpal/callback/<str:db_alias>/", ZarinpalCallbackView.as_view(), name="zarinpal-callback"),
    path("delivery-method/", SelectDeliveryMethodView.as_view(), name="order-delivery-method"),
]

router = routers.DefaultRouter()
router.register(r'cart/items', CartItemViewSet, basename='cart-item')
urlpatterns += router.urls
