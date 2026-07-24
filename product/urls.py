from django.urls import path
from rest_framework import routers

from product.views import BrandListView, CategoryListView, ProductListView

urlpatterns = [
    path("brands/", BrandListView.as_view()),
    path("categories/", CategoryListView.as_view()),
    path("products/", ProductListView.as_view()),
]