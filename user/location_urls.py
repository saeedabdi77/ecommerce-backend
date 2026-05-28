from django.urls import path
from .views import ProvinceView, CityView


urlpatterns = [
    path("provinces/", ProvinceView.as_view()),
    path("provinces/<int:province__id>/citites/", CityView.as_view()),
]
