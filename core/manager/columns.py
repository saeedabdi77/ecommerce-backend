from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class Column:
    def __init__(self, name, label=None, *, value=None, formatter=None, editable=None, sortable=False, html=False):
        self.name = name
        self.label = label or name.replace("_", " ").title()
        self.value = value
        self.formatter = formatter
        self.sortable = sortable
        self.editable = editable
        self.html = html

    @property
    def ordering_name(self):
        return self.name.replace(".", "__")

    def get_value(self, obj):
        if self.value:
            return self.value(obj)

        value = obj

        for part in self.name.split("."):
            if value is None:
                return None

            value = getattr(value, part, None)

            if callable(value):
                value = value()

        return value

    def render(self, obj):
        value = self.get_value(obj)

        if self.formatter:
            value = self.formatter(value, obj)

        if value is None:
            return ""

        return mark_safe(value) if self.html else conditional_escape(str(value))

    def get_edit_url(self, request, manager, obj):
        return manager.get_update_url(request, obj)
