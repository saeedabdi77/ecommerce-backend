from django.urls import path

from core.manager.managers import registry
from core.manager.views import (
    ManagerActionView,
    ManagerAutocompleteView,
    ManagerBulkActionView,
    ManagerCreateView,
    ManagerDashboardView,
    ManagerDeleteView,
    ManagerDetailView,
    ManagerFieldUpdateView,
    ManagerListView,
    ManagerLoginView,
    ManagerLogoutView,
    ManagerUpdateView,
)

app_name = "manager"

urlpatterns = [
    path("login/", ManagerLoginView.as_view(), name="login"),
    path("logout/", ManagerLogoutView.as_view(), name="logout"),
    path("", ManagerDashboardView.as_view(), name="dashboard"),
    path(
        "autocomplete/<str:app_label>/<str:model_name>/",
        ManagerAutocompleteView.as_view(),
        name="autocomplete",
    ),
]

for manager in registry.all():
    urlpatterns.extend([
        path(f"{manager.slug}/", ManagerListView.as_view(manager=manager), name=f"{manager.slug}-list"),
        path(f"{manager.slug}/create/", ManagerCreateView.as_view(manager=manager), name=f"{manager.slug}-create"),
        path(f"{manager.slug}/<int:pk>/", ManagerDetailView.as_view(manager=manager), name=f"{manager.slug}-detail"),
        path(f"{manager.slug}/<int:pk>/edit/", ManagerUpdateView.as_view(manager=manager), name=f"{manager.slug}-update"),
        path(f"{manager.slug}/<int:pk>/delete/", ManagerDeleteView.as_view(manager=manager), name=f"{manager.slug}-delete"),
        path(f"{manager.slug}/<int:pk>/action/<slug:action>/", ManagerActionView.as_view(manager=manager), name=f"{manager.slug}-action"),
        path(f"{manager.slug}/bulk/<slug:action>/", ManagerBulkActionView.as_view(manager=manager), name=f"{manager.slug}-bulk-action"),
        path(f"{manager.slug}/update-fields/", ManagerFieldUpdateView.as_view(manager=manager), name=f"{manager.slug}-update-fields"),
    ])
