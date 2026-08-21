from django.urls import path

from core.manager.managers import registry
from core.manager.views import ManagerActionView, ManagerBulkActionView, ManagerCreateView, ManagerDeleteView, \
    ManagerDetailView, ManagerListView, ManagerUpdateView, ManagerDashboardView, ManagerLoginView, \
    ManagerFieldUpdateView

app_name = "manager"

urlpatterns = []

for manager in registry.all():
    urlpatterns.extend([
        path("login/", ManagerLoginView.as_view(), name="login"),
        path("", ManagerDashboardView.as_view(), name="dashboard"),
        path(f"{manager.slug}/", ManagerListView.as_view(manager=manager), name=f"{manager.slug}-list"),
        path(f"{manager.slug}/create/", ManagerCreateView.as_view(manager=manager), name=f"{manager.slug}-create"),
        path(f"{manager.slug}/<int:pk>/", ManagerDetailView.as_view(manager=manager), name=f"{manager.slug}-detail"),
        path(f"{manager.slug}/<int:pk>/edit/", ManagerUpdateView.as_view(manager=manager), name=f"{manager.slug}-update"),
        path(f"{manager.slug}/<int:pk>/delete/", ManagerDeleteView.as_view(manager=manager), name=f"{manager.slug}-delete"),
        path(f"{manager.slug}/<int:pk>/action/<slug:action>/", ManagerActionView.as_view(manager=manager), name=f"{manager.slug}-action"),
        path(f"{manager.slug}/bulk/<slug:action>/", ManagerBulkActionView.as_view(manager=manager), name=f"{manager.slug}-bulk-action"),
        path(f"{manager.slug}/update-fields/", ManagerFieldUpdateView.as_view(manager=manager), name=f"{manager.slug}-update-fields"),
    ])