from django.urls import path

from product.views import BrandListView, CategoryListView, ProductDetailView, ProductListView

urlpatterns = [
    path("brands/", BrandListView.as_view()),
    path("categories/", CategoryListView.as_view()),
    path("products/", ProductListView.as_view()),
    path("products/<slug:slug>/", ProductDetailView.as_view()),
]