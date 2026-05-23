from django.urls import path

from rest_framework import routers

from product.views import TestView


urlpatterns = [
    path('test', TestView.as_view(), name='test'),

]
