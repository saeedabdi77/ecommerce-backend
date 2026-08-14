from django.urls import path

from order.views import CartRetrieveView

urlpatterns = [
    path("cart/", CartRetrieveView.as_view()),
]
