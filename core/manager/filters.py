from django import forms
from django.db.models import Q


class Filter:
    field_class = forms.CharField

    def __init__(self, name, label=None, *, lookup=None):
        self.name = name
        self.label = label or name.replace("_", " ").title()
        self.lookup = lookup

    def get_form_field(self):
        return self.field_class(label=self.label, required=False)

    def apply(self, queryset, value):
        if value in (None, "", []):
            return queryset

        lookup = f"__{self.lookup}" if self.lookup else ""
        return queryset.filter(**{f"{self.name}{lookup}": value})


class TextFilter(Filter):
    def __init__(self, name, label=None, *, lookup="icontains"):
        super().__init__(name, label, lookup=lookup)


class ChoiceFilter(Filter):
    def __init__(self, name, choices, label=None, *, lookup=None):
        super().__init__(name, label, lookup=lookup)
        self.choices = choices

    def get_form_field(self):
        return forms.ChoiceField(label=self.label, required=False, choices=(("", "---------"), *self.choices))


class BooleanFilter(Filter):
    def get_form_field(self):
        return forms.NullBooleanField(label=self.label, required=False)


class DateFilter(Filter):
    def get_form_field(self):
        return forms.DateField(label=self.label, required=False, widget=forms.DateInput(attrs={"type": "date"}))


class DateTimeFilter(Filter):
    def get_form_field(self):
        return forms.DateTimeField(label=self.label, required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))


class ForeignKeyFilter(Filter):
    def __init__(self, name, queryset, label=None, *, lookup=None):
        super().__init__(name, label, lookup=lookup)
        self.queryset = queryset

    def get_form_field(self):
        return forms.ModelChoiceField(label=self.label, required=False, queryset=self.queryset)

    def apply(self, queryset, value):
        if value is None:
            return queryset

        lookup = f"__{self.lookup}" if self.lookup else ""
        return queryset.filter(**{f"{self.name}{lookup}_id": value.pk})


class ManyToManyFilter(ForeignKeyFilter):
    def apply(self, queryset, value):
        if value is None:
            return queryset

        return queryset.filter(**{f"{self.name}__id": value.pk}).distinct()


class FilterSet:
    def __init__(self, filters, data=None):
        self.filters = tuple(filters)
        self.form = self._build_form(data)

    def _build_form(self, data):
        fields = {filter_.name: filter_.get_form_field() for filter_ in self.filters}
        form_class = type("ManagerFilterForm", (forms.Form,), fields)
        return form_class(data=data)

    def apply(self, queryset):
        if not self.form.is_valid():
            return queryset

        for filter_ in self.filters:
            queryset = filter_.apply(queryset, self.form.cleaned_data.get(filter_.name))

        return queryset


class Search:
    def __init__(self, fields):
        self.fields = tuple(fields)

    def apply(self, queryset, value):
        if not value or not self.fields:
            return queryset

        query = Q()

        for field in self.fields:
            query |= Q(**{f"{field}__icontains": value})

        return queryset.filter(query)


class Ordering:
    def __init__(self, fields):
        self.fields = tuple(fields)

    def apply(self, queryset, value):
        if not value:
            return queryset

        descending = value.startswith("-")
        field = value[1:] if descending else value

        if field not in self.fields:
            return queryset

        return queryset.order_by(f"-{field}" if descending else field)
