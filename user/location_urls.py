from django.urls import path
from .views import ProvinceView, CityView


urlpatterns = [
    path("provinces/", ProvinceView.as_view()),
    path("provinces/<int:province_id>/cities/", CityView.as_view()),
]
