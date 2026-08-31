from django.contrib import messages
from django.shortcuts import redirect


class Action:
    name = None
    label = None
    method = "post"
    confirm = False
    confirmation_message = "Are you sure?"

    def __init__(self, name=None, label=None, *, confirm=False):
        self.name = name or self.name
        self.label = label or self.label or self.name
        self.confirm = confirm

    def is_visible(self, request, manager, obj=None):
        return self.has_permission(request, manager, obj)

    def has_permission(self, request, manager, obj=None):
        permission = manager.get_permission(request)
        return permission is None or permission.can_action(request, manager, self, obj)

    def execute(self, request, manager, obj=None):
        raise NotImplementedError

    def get_url(self, request, manager, obj=None):
        raise NotImplementedError


class CreateAction(Action):
    name = "create"
    label = "ایجاد"

    def __init__(self, form_class, **kwargs):
        super().__init__(**kwargs)
        self.form_class = form_class

    def get_url(self, request, manager, obj=None):
        return manager.get_create_url(request)


class UpdateAction(Action):
    name = "update"
    label = "ویرایش"

    def __init__(self, form_class, **kwargs):
        super().__init__(**kwargs)
        self.form_class = form_class

    def get_url(self, request, manager, obj=None):
        return manager.get_update_url(request, obj)


class DetailAction(Action):
    name = "detail"
    label = "نمایش"

    def get_url(self, request, manager, obj=None):
        return manager.get_detail_url(request, obj)


class DeleteAction(Action):
    name = "delete"
    label = "حذف"
    confirmation_message = "آیا از حذف این مورد اطمینان دارید؟"

    def __init__(self, *, confirm=True, **kwargs):
        super().__init__(**kwargs)
        self.confirm = confirm

    def get_url(self, request, manager, obj=None):
        return manager.get_delete_url(request, obj)

    def execute(self, request, manager, obj=None):
        obj.delete()
        messages.success(request, "مورد با موفقیت حذف شد.")
        return redirect(manager.get_list_url(request))


class CustomAction(Action):
    def __init__(self, name, label, handler, *, confirm=False, confirmation_message="Are you sure?"):
        super().__init__(name, label, confirm=confirm)
        self.handler = handler
        self.confirmation_message = confirmation_message

    def get_url(self, request, manager, obj=None):
        return manager.get_custom_action_url(request, obj, self.name)


class BulkAction(Action):
    bulk = True

    def __init__(self, name, label, handler, *, confirm=False, confirmation_message="Are you sure?"):
        super().__init__(name, label, confirm=confirm)
        self.handler = handler
        self.confirmation_message = confirmation_message

    def get_url(self, request, manager, obj=None):
        return manager.get_bulk_action_url(request, self.name)
