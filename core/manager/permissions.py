class BasePermission:
    def can_view(self, request, manager):
        return True

    def can_create(self, request, manager):
        return True

    def can_update(self, request, manager, obj=None):
        return True

    def can_delete(self, request, manager, obj=None):
        return True

    def can_detail(self, request, manager, obj=None):
        return True

    def can_action(self, request, manager, action, obj=None):
        return True


class ModelPermission(BasePermission):
    def _has_perm(self, request, manager, action):
        opts = manager.model._meta
        return request.user.has_perm(f"{opts.app_label}.{action}_{opts.model_name}")

    def can_view(self, request, manager):
        return self._has_perm(request, manager, "view")

    def can_create(self, request, manager):
        return self._has_perm(request, manager, "add")

    def can_update(self, request, manager, obj=None):
        return self._has_perm(request, manager, "change")

    def can_delete(self, request, manager, obj=None):
        return self._has_perm(request, manager, "delete")

    def can_detail(self, request, manager, obj=None):
        return self.can_view(request, manager)
