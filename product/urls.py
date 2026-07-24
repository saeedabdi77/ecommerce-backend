from django.urls import path
from rest_framework import routers

from product.views import BrandListView, CategoryListView

urlpatterns = [
    path("brands/", BrandListView.as_view()),
    path("categories/", CategoryListView.as_view()),
]