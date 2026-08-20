from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse


class BaseManager:
    model = None
    title = None
    columns = ()
    filters = ()
    actions = ()
    search_fields = ()
    ordering = ()
    select_related = ()
    prefetch_related = ()
    paginate_by = 25
    permission = None
    list_template = "manager/list.html"
    form_template = "manager/form.html"
    detail_template = "manager/detail.html"
    confirm_template = "manager/confirm.html"

    def __init__(self):
        if self.model is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__}.model must be defined.")

    def get_title(self):
        return self.title or self.model._meta.verbose_name_plural.title()

    def get_queryset(self, request):
        queryset = self.model._default_manager.all()

        if self.select_related:
            queryset = queryset.select_related(*self.select_related)

        if self.prefetch_related:
            queryset = queryset.prefetch_related(*self.prefetch_related)

        return queryset

    def get_columns(self, request):
        return self.columns

    def get_filters(self, request):
        return self.filters

    def get_actions(self, request, obj=None):
        return tuple(action for action in self.actions if action.is_visible(request, self, obj))

    def get_action(self, name):
        return next((action for action in self.actions if action.name == name), None)

    def get_search_fields(self, request):
        return self.search_fields

    def get_ordering(self, request):
        return self.ordering

    def get_paginate_by(self, request):
        return self.paginate_by

    def get_permission(self, request):
        return self.permission

    def get_list_url(self, request):
        return reverse(f"manager:{self.slug}-list")

    def get_create_url(self, request):
        return reverse(f"manager:{self.slug}-create")

    def get_detail_url(self, request, obj):
        return reverse(f"manager:{self.slug}-detail", kwargs={"pk": obj.pk})

    def get_update_url(self, request, obj):
        return reverse(f"manager:{self.slug}-update", kwargs={"pk": obj.pk})

    def get_delete_url(self, request, obj):
        return reverse(f"manager:{self.slug}-delete", kwargs={"pk": obj.pk})


class ManagerRegistry:
    def __init__(self):
        self._managers = {}

    def register(self, manager):
        instance = manager() if isinstance(manager, type) else manager
        self._managers[instance.slug] = instance
        return manager

    def get(self, slug):
        return self._managers[slug]

    def all(self):
        return self._managers.values()


registry = ManagerRegistry()
