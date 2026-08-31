from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from core.manager.filters import FilterSet, Ordering, Search
from core.manager.forms import apply_autocomplete, get_form_fieldsets
from core.manager.managers import registry
from core.manager.pagination import get_page_window
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
        return registry.get_menu(self.request)

    def get_base_context(self, **extra):
        manager = self.get_manager()
        context = {
            "manager": manager,
            "menu": self.get_navigation(),
            "list_url": manager.get_list_url(self.request),
            "dashboard_url": get_manager_root_url(self.request),
            "logout_url": f"{get_manager_root_url(self.request)}logout/",
            "is_dashboard": False,
        }
        context.update(extra)
        return context


class ManagerLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "manager/login.html", {"next": request.GET.get("next", "")})

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "manager/login.html", {
                "error": "نام کاربری یا رمز عبور اشتباه است.",
                "next": request.POST.get("next", ""),
            })

        login(request, user)

        return redirect(request.POST.get("next") or request.path.rsplit("login/", 1)[0])


class ManagerLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(get_manager_root_url(request))

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(get_manager_root_url(request))


class ManagerDashboardView(ManagerViewMixin, View):
    manager = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{get_manager_root_url(request)}login/"
            return redirect(f"{login_url}?next={request.get_full_path()}")
        return super().dispatch(request, *args, **kwargs)

    def get_manager(self):
        return None

    def get(self, request, *args, **kwargs):
        cards = []

        for manager in registry.all():
            if not manager.menu or not manager.can_access(request):
                continue

            cards.append({
                "manager": manager,
                "label": manager.get_menu_label(),
                "icon": manager.get_menu_icon(),
                "url": manager.get_list_url(request),
                "count": manager.get_queryset(request).values("pk").count(),
            })

        return render(request, "manager/dashboard.html", {
            "menu": registry.get_menu(request),
            "dashboard_url": request.path,
            "logout_url": f"{get_manager_root_url(request)}logout/",
            "is_dashboard": True,
            "cards": cards,
        })


class ManagerListView(ManagerViewMixin, View):
    def _get_editable_columns(self, request):
        return {
            column.name: column
            for column in self.get_manager().get_columns(request)
            if column.editable
        }

    def _build_column_meta(self, manager, columns):
        model = manager.model
        meta = []

        for index, column in enumerate(columns):
            model_field = column.get_model_field(model)
            edit_widget = column.get_edit_widget(model)
            meta.append({
                "column": column,
                "edit_widget": edit_widget,
                "edit_choices": column.get_edit_choices(model) if edit_widget == "select" else None,
                "use_boolean_badge": isinstance(model_field, models.BooleanField) and not column.editable,
                "is_primary": index == 0,
            })

        return meta

    def _save_inline_edits(self, request):
        manager = self.get_manager()
        editable_columns = self._get_editable_columns(request)
        page_pks = request.POST.getlist("_page_pks")

        if page_pks:
            objects = self.get_queryset().filter(pk__in=page_pks)
        else:
            objects = [
                obj for obj in self.get_queryset()
                if any(f"{field_name}__{obj.pk}" in request.POST for field_name in editable_columns)
            ]

        updated = False

        for obj in objects:
            update_fields = []

            for field_name, column in editable_columns.items():
                key = f"{field_name}__{obj.pk}"
                field = manager.model._meta.get_field(column.get_field_name())

                if isinstance(field, models.BooleanField):
                    value = request.POST.get(key) == "1"
                    if getattr(obj, field_name) != value:
                        setattr(obj, field_name, value)
                        update_fields.append(field_name)
                elif key in request.POST:
                    value = field.to_python(request.POST[key])
                    if getattr(obj, field_name) != value:
                        setattr(obj, field_name, value)
                        update_fields.append(field_name)

            if update_fields:
                obj.save(update_fields=update_fields)
                updated = True

        return updated

    def post(self, request, *args, **kwargs):
        self.check_permission("edit")

        if self._save_inline_edits(request):
            messages.success(request, "تغییرات ذخیره شد.")

        return redirect(request.get_full_path())

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

        total_count = queryset.count()
        paginate_by = manager.get_paginate_by(request)
        paginator = Paginator(queryset, paginate_by) if paginate_by else None
        page_obj = paginator.get_page(request.GET.get("page")) if paginator else None
        objects = list(page_obj.object_list) if page_obj else list(queryset[:paginate_by] if paginate_by else queryset)

        columns = manager.get_columns(request)
        column_meta = self._build_column_meta(manager, columns)
        detail_action = manager.get_action("detail")

        toolbar_actions = []
        bulk_actions = []

        for action in manager.get_actions(request):
            if not action.is_visible(request, manager):
                continue

            if action.name == "create":
                toolbar_actions.append({
                    "action": action,
                    "url": action.get_url(request, manager),
                })
            elif getattr(action, "bulk", False):
                bulk_actions.append({
                    "action": action,
                    "url": manager.get_bulk_action_url(request, action.name),
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

            detail_url = detail_action.get_url(request, manager, obj) if detail_action else None

            rows.append({
                "object": obj,
                "detail_url": detail_url,
                "cells": [
                    {
                        "column": item["column"],
                        "value": item["column"].render(obj, manager.model),
                        "raw_value": item["column"].get_value(obj),
                        "edit_widget": item["edit_widget"],
                        "edit_choices": item["edit_choices"],
                        "is_primary": item["is_primary"],
                    }
                    for item in column_meta
                ],
                "actions": row_actions,
            })

        if page_obj:
            start_index = (page_obj.number - 1) * paginate_by + 1
            end_index = start_index + len(objects) - 1
        else:
            start_index = 1 if total_count else 0
            end_index = total_count

        active_filters = filter_set.get_active_filters()

        if search:
            active_filters.insert(0, {
                "name": "search",
                "label": "جستجو",
                "value": search,
            })

        search_fields = manager.get_search_fields(request)

        context = self.get_base_context(
            objects=objects,
            page_obj=page_obj,
            page_window=get_page_window(page_obj) if page_obj else [],
            paginate_by=paginate_by,
            paginate_by_options=manager.paginate_by_options,
            filter_form=filter_set.form,
            search=search,
            has_search=bool(search_fields),
            search_placeholder=manager.get_search_placeholder(request),
            columns=columns,
            actions=toolbar_actions,
            bulk_actions=bulk_actions,
            rows=rows,
            current_ordering=ordering or "",
            active_filters=active_filters,
            total_count=total_count,
            start_index=start_index,
            end_index=end_index,
            has_active_filters=bool(active_filters),
            page_pks=[str(obj.pk) for obj in objects],
        )

        return render(request, manager.list_template, context)


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
        form = action.form_class()
        apply_autocomplete(form)

        return render(request, manager.form_template, self.get_base_context(
            action=action,
            form=form,
            fieldsets=get_form_fieldsets(form),
            breadcrumb_action=action.label,
        ))

    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("create")
        form = action.form_class(request.POST, request.FILES)
        apply_autocomplete(form)

        if form.is_valid():
            form.save()
            messages.success(request, "مورد جدید با موفقیت ایجاد شد.")
            return redirect(manager.get_list_url(request))

        return render(request, manager.form_template, self.get_base_context(
            action=action,
            form=form,
            fieldsets=get_form_fieldsets(form),
            breadcrumb_action=action.label,
        ))


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
        form = action.form_class(instance=obj)
        apply_autocomplete(form)

        return render(request, manager.form_template, self.get_base_context(
            action=action,
            form=form,
            object=obj,
            fieldsets=get_form_fieldsets(form),
            breadcrumb_action=action.label,
        ))

    def post(self, request, *args, **kwargs):
        manager = self.get_manager()
        action = manager.get_action("update")
        obj = self.get_object()
        form = action.form_class(request.POST, request.FILES, instance=obj)
        apply_autocomplete(form)

        if form.is_valid():
            form.save()
            messages.success(request, "تغییرات با موفقیت ذخیره شد.")
            return redirect(manager.get_list_url(request))

        return render(request, manager.form_template, self.get_base_context(
            action=action,
            form=form,
            object=obj,
            fieldsets=get_form_fieldsets(form),
            breadcrumb_action=action.label,
        ))


class ManagerDetailView(ManagerViewMixin, View):
    def get(self, request, *args, **kwargs):
        manager = self.get_manager()
        obj = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        self.check_permission("detail", obj)

        fields = [
            {"label": column.label, "value": column.render(obj, manager.model)}
            for column in manager.get_columns(request)
        ]

        actions = [
            {"action": action, "url": action.get_url(request, manager, obj), "danger": action.name == "delete"}
            for action in manager.get_actions(request, obj)
            if action.is_visible(request, manager, obj)
        ]

        return render(request, manager.detail_template, self.get_base_context(
            object=obj,
            fields=fields,
            actions=actions,
            breadcrumb_action="نمایش",
        ))


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
        action = manager.get_action("delete")

        return render(request, manager.confirm_template, self.get_base_context(
            action=action,
            object=self.get_object(),
            breadcrumb_action=action.label,
        ))

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
        self.check_permission("edit")

        editable_columns = {
            column.name: column
            for column in manager.get_columns(request)
            if column.editable
        }

        page_pks = request.POST.getlist("_page_pks") or request.POST.getlist("selected")

        if not page_pks:
            return redirect(request.META.get("HTTP_REFERER", manager.get_list_url(request)))

        for obj in self.get_queryset().filter(pk__in=page_pks):
            update_fields = []

            for field_name, column in editable_columns.items():
                key = f"{field_name}__{obj.pk}"
                field = manager.model._meta.get_field(column.get_field_name())

                if isinstance(field, models.BooleanField):
                    value = request.POST.get(key) == "1"
                    if getattr(obj, field_name) != value:
                        setattr(obj, field_name, value)
                        update_fields.append(field_name)
                elif key in request.POST:
                    value = field.to_python(request.POST[key])
                    if getattr(obj, field_name) != value:
                        setattr(obj, field_name, value)
                        update_fields.append(field_name)

            if update_fields:
                obj.save(update_fields=update_fields)

        messages.success(request, "تغییرات ذخیره شد.")
        return redirect(request.META.get("HTTP_REFERER", manager.get_list_url(request)))


class ManagerAutocompleteView(View):
    def get(self, request, app_label, model_name, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(get_manager_root_url(request))

        from django.http import JsonResponse

        from core.manager.autocomplete import search_models, uses_autocomplete
        from core.manager.autocomplete import get_model as get_autocomplete_model

        model = get_autocomplete_model(app_label, model_name)

        if not uses_autocomplete(model):
            return JsonResponse({"results": []})

        query = request.GET.get("q", "").strip()
        pk = request.GET.get("pk")

        if pk:
            results = search_models(app_label, model_name, pk=pk, limit=1)
        elif len(query) < 2:
            return JsonResponse({"results": []})
        else:
            results = search_models(app_label, model_name, query=query)

        return JsonResponse({"results": results})
