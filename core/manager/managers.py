from django.core.exceptions import ImproperlyConfigured

from core.manager.utils import get_manager_url


class ManagerPermission:
    def can_view(self, request, manager, obj=None):
        return request.user.is_superuser

    def can_create(self, request, manager, obj=None):
        return request.user.is_superuser

    def can_edit(self, request, manager, obj=None):
        return request.user.is_superuser

    def can_delete(self, request, manager, obj=None):
        return request.user.is_superuser

    def can_detail(self, request, manager, obj=None):
        return request.user.is_superuser

    def can_action(self, request, manager, action, obj=None):
        return request.user.is_superuser


class BaseManager:
    permission_class = ManagerPermission

    menu = True
    menu_group = None
    menu_label = None
    menu_icon = None
    menu_parent = None
    menu_order = 0

    model = None
    title = None
    columns = ()
    filters = ()
    actions = ()
    search_fields = ()
    search_placeholder = None
    ordering = ()
    select_related = ()
    prefetch_related = ()
    paginate_by = 25
    paginate_by_options = (25, 50, 100)

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

    def get_search_placeholder(self, request):
        if self.search_placeholder:
            return self.search_placeholder

        if not self.search_fields:
            return ""

        labels = []

        for field_name in self.search_fields:
            part = field_name.split("__")[0]

            for column in self.columns:
                column_field = column.name.split(".")[0]

                if column_field == part or column.name.replace(".", "__") == field_name:
                    labels.append(column.label)
                    break
            else:
                labels.append(part.replace("_", " "))

        if not labels:
            return "جستجو در رکوردها..."

        return "جستجو در: " + "، ".join(dict.fromkeys(labels))

    def get_ordering(self, request):
        return self.ordering

    def get_paginate_by(self, request):
        per_page = request.GET.get("per_page")

        if per_page and str(per_page).isdigit():
            value = int(per_page)

            if value in self.paginate_by_options:
                return value

        return self.paginate_by

    def get_permission(self, request):
        return self.permission_class()

    def can_access(self, request):
        permission = self.get_permission(request)
        return permission is None or permission.can_view(request, self)

    def get_manager_url(self, request):
        return get_manager_url(request, self.slug)

    def get_list_url(self, request):
        return self.get_manager_url(request)

    def get_create_url(self, request):
        return f"{self.get_manager_url(request)}create/"

    def get_detail_url(self, request, obj):
        return f"{self.get_manager_url(request)}{obj.pk}/"

    def get_update_url(self, request, obj):
        return f"{self.get_manager_url(request)}{obj.pk}/edit/"

    def get_delete_url(self, request, obj):
        return f"{self.get_manager_url(request)}{obj.pk}/delete/"

    def get_menu_label(self):
        return self.menu_label or self.get_title()

    def get_menu_icon(self):
        return self.menu_icon

    def get_menu_group(self):
        return self.menu_group

    def get_menu_parent(self):
        return self.menu_parent

    def get_menu_order(self):
        return self.menu_order

    def get_menu_items(self, request):
        if not self.menu or not self.can_access(request):
            return []

        return [{
            "manager": self,
            "label": self.get_menu_label(),
            "icon": self.get_menu_icon(),
            "url": self.get_list_url(request),
            "order": self.get_menu_order(),
            "children": [],
        }]


class ManagerRegistry:
    def __init__(self):
        self._managers = {}

    def register(self, manager):
        instance = manager() if isinstance(manager, type) else manager
        self._managers[instance.slug] = instance
        return manager

    def get(self, slug):
        return self._managers.get(slug)

    def all(self):
        return self._managers.values()

    def get_menu_group(self, key):
        return next((group for group in menu_groups if group.key == key), None)

    def get_menu(self, request):
        groups = {}

        for manager in self.all():
            if not manager.menu or not manager.can_access(request):
                continue

            group_key = manager.get_menu_group()

            if not group_key:
                continue

            group = self.get_menu_group(group_key)

            if group is None:
                continue

            groups.setdefault(group_key, {"group": group, "items": []})

            groups[group_key]["items"].append({
                "manager": manager,
                "label": manager.get_menu_label(),
                "icon": manager.get_menu_icon(),
                "url": manager.get_list_url(request),
                "order": manager.get_menu_order(),
                "children": [],
            })

        for group_data in groups.values():
            items = group_data["items"]

            root_items = [
                item for item in items
                if not item["manager"].get_menu_parent()
            ]

            for item in root_items:
                parent_slug = item["manager"].slug

                item["children"] = sorted(
                    [
                        child for child in items
                        if child["manager"].get_menu_parent() == parent_slug
                    ],
                    key=lambda child: child["order"],
                )

            group_data["items"] = sorted(root_items, key=lambda item: item["order"])

        return sorted(groups.values(), key=lambda group: group["group"].order)


class MenuGroup:
    def __init__(self, key, label, icon=None, order=0):
        self.key = key
        self.label = label
        self.icon = icon
        self.order = order


menu_groups = [
    MenuGroup("product_management", "مدیریت محصول", order=10),
    MenuGroup("inventory", "موجودی انبار", order=20),
    MenuGroup("customers", "مشتریان", order=30),
    MenuGroup("users", "کاربران", order=35),
    MenuGroup("orders", "سفارش‌ها", order=38),
    MenuGroup("repair", "تعمیرات", order=40),
    MenuGroup("installation", "نصب", order=50),
]


registry = ManagerRegistry()
