from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from core.manager.filters import FilterSet, Ordering, Search
from core.manager.managers import registry
from core.manager.utils import get_manager_root_url


class ManagerViewMixin:
    manager = None

    def dispatch(self, request, *args, **kwargs):
        response = self.check_authentication()

        if response:
            return response

        return super().dispatch(request, *args, **kwargs)

    def get_manager(self):
        if self.manager is None:
            raise AttributeError("manager must be defined.")
        return self.manager

    def get_queryset(self):
        return self.get_manager().get_queryset(self.request)

    def get_login_url(self):
        return f"{get_manager_root_url(self.request)}login/"

    def check_authentication(self):
        if not self.request.user.is_authenticated:
            login_url = self.get_login_url()
            next_url = self.request.get_full_path()
            return redirect(f"{login_url}?next={next_url}")
        return None

    def check_permission(self, action, obj=None):
        permission = self.get_manager().get_permission(self.request)

        if permission and not getattr(permission, f"can_{action}")(self.request, self.get_manager(), obj):
            raise PermissionDenied

    def get_navigation(self):
        navigation = []

        for manager in registry.all():
            navigation.append({
                "label": manager.get_title(),
                "url": manager.get_list_url(self.request),
                "active": manager.slug == self.get_manager().slug,
            })

        return navigation

    def get_login_url(self):
        return f"{get_manager_root_url(self.request)}login/"


class ManagerLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "manager/login.html", {"next": request.GET.get("next", "")})

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "manager/login.html", {
                "error": "Invalid username or password.",
                "next": request.POST.get("next", ""),
            })

        login(request, user)

        return redirect(request.POST.get("next") or request.path.rsplit("login/", 1)[0])


class ManagerDashboardView(ManagerViewMixin, View):
    def get(self, request, *args, **kwargs):
        menu = registry.get_menu(request)

        return render(request, "manager/dashboard.html", {
            "menu": menu,
            "dashboard_url": request.path,
            "is_dashboard": True,
        })


class ManagerListView(ManagerViewMixin, View):
    def get(self, request, *args, **kwargs):
        manager = self.get_manager()
        self.check_permission("view")

        queryset = self.get_queryset()

        search = request.GET.get("search")
        if search:
            queryset = Search(manager.get_search_fields(request)).apply(queryset, search)

        filter_set = FilterSet(manager.get_filters(request), request.GET)
        queryset = filter_set.apply(queryset)

        ordering = request.GET.get("ordering")
        if ordering:
            fields = {column.ordering_name for column in manager.get_columns(request) if column.sortable}
            queryset = Ordering(fields).apply(queryset, ordering)
        elif manager.get_ordering(request):
            queryset = queryset.order_by(*manager.get_ordering(request))

        paginate_by = manager.get_paginate_by(request)
        paginator = Paginator(queryset, paginate_by) if paginate_by else None
        page_obj = paginator.get_page(request.GET.get("page")) if paginator else None
        objects = page_obj.object_list if page_obj else queryset

        columns = manager.get_columns(request)

        manager_actions = [
            action for action in manager.get_actions(request)
            if action.is_visible(request, manager)
        ]

        actions = []

        for action in manager_actions:
            if action.name == "create":
                actions.append({
                    "action": action,
                    "url": action.get_url(request, manager),
                })

        rows = []

        for obj in objects:
            row_actions = []

            for action in manager.get_actions(request, obj):
                if not action.is_visible(request, manager, obj):
                    continue

                row_actions.append({
                    "action": action,
                    "url": action.get_url(request, manager, obj),
                    "danger": action.name == "delete",
                })

            rows.append({
                "object": obj,
                "cells": [column.render(obj) for column in columns],
                "actions": row_actions,
            })

        return render(request, manager.list_template, {
            "manager": manager,
            "objects": objects,
            "page_obj": page_obj,
            "filter_form": filter_set.form,
            "search": search,
            "columns": columns,
            "actions": actions,
            "rows": rows,
            "managers": self.get_navigation(),
        })


class ManagerCreateView(ManagerViewMixin, View):
    def dispatch(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("create")

        if action is None or not action.has_permission(request, manager):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("create")

        return render(request, manager.form_template, {
            "manager": manager,
            "action": action,
            "form": action.form_class(),
            "managers": self.get_navigation(),
        })

    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("create")
        form = action.form_class(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save()
            return redirect(manager.get_list_url(request))

        return render(request, manager.form_template, {
            "manager": manager,
            "action": action,
            "form": form,
            "managers": self.get_navigation(),
        })


class ManagerUpdateView(ManagerViewMixin, View):
    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("update")
        obj = self.get_object()

        if action is None or not action.has_permission(request, manager, obj):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("update")
        obj = self.get_object()

        return render(request, manager.form_template, {
            "manager": manager,
            "action": action,
            "form": action.form_class(instance=obj),
            "object": obj,
            "managers": self.get_navigation(),
        })

    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("update")
        obj = self.get_object()
        form = action.form_class(request.POST, request.FILES, instance=obj)

        if form.is_valid():
            obj = form.save()
            return redirect(manager.get_list_url(request))

        return render(request, manager.form_template, {
            "manager": manager,
            "action": action,
            "form": form,
            "object": obj,
            "managers": self.get_navigation(),
        })


class ManagerDetailView(ManagerViewMixin, View):
    def get(self, request, *args, **kwargs):
        manager = self.get_manager()
        obj = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        self.check_permission("detail", obj)

        fields = [
            {"label": column.label, "value": column.render(obj)}
            for column in manager.get_columns(request)
        ]

        actions = [
            {"action": action, "url": action.get_url(request, manager, obj), "danger": action.name == "delete"}
            for action in manager.get_actions(request, obj)
            if action.is_visible(request, manager, obj)
        ]

        return render(request, manager.detail_template, {
            "manager": manager,
            "object": obj,
            "fields": fields,
            "actions": actions,
            "managers": self.get_navigation(),
        })


class ManagerDeleteView(ManagerViewMixin, View):
    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("delete")
        obj = self.get_object()

        if action is None or not action.has_permission(request, manager, obj):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        manager = self.get_manager()

        return render(request, manager.confirm_template, {
            "manager": manager,
            "action": manager.get_action("delete"),
            "object": self.get_object(),
            "managers": self.get_navigation(),
        })

    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        return manager.get_action("delete").execute(request, manager, self.get_object())


class ManagerActionView(ManagerViewMixin, View):
    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action(kwargs["action"])
        obj = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])

        if action is None or not action.has_permission(request, manager, obj):
            raise PermissionDenied

        return action.handler(request, obj)


class ManagerBulkActionView(ManagerViewMixin, View):
    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action(kwargs["action"])

        if action is None or not getattr(action, "bulk", False) or not action.has_permission(request, manager):
            raise PermissionDenied

        queryset = self.get_queryset().filter(pk__in=request.POST.getlist("selected"))

        return action.handler(request, queryset)


class ManagerFieldUpdateView(ManagerViewMixin, View):
    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        obj = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        field_name = kwargs["field"]

        column = next(
            (column for column in manager.get_columns(request) if column.field == field_name and column.editable),
            None,
        )

        if column is None:
            raise PermissionDenied

        self.check_permission("edit", obj)

        field = manager.model._meta.get_field(field_name)
        value = field.to_python(request.POST.get("value"))

        setattr(obj, field_name, value)
        obj.save(update_fields=[field_name])

        return redirect(request.META.get("HTTP_REFERER", manager.get_list_url(request)))
