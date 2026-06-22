from django_filters import filters
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema


class DjangoFilterAutoSchema(SwaggerAutoSchema):
    def get_filter_parameters(self):
        parameters = super().get_filter_parameters()

        filterset_class = getattr(self.view, "filterset_class", None)
        if not filterset_class:
            return parameters

        for name, filter_instance in filterset_class.base_filters.items():
            if any(parameter.name == name for parameter in parameters):
                continue

            parameter_type = self.get_filter_type(filter_instance)
            parameter_format = self.get_filter_format(filter_instance)

            parameters.append(
                openapi.Parameter(
                    name=name,
                    in_=openapi.IN_QUERY,
                    description=getattr(filter_instance, "label", None) or name,
                    type=parameter_type,
                    format=parameter_format,
                    required=getattr(filter_instance, "required", False),
                )
            )

        return parameters

    def get_filter_type(self, filter_instance):
        if isinstance(filter_instance, filters.NumberFilter):
            return openapi.TYPE_NUMBER

        if isinstance(filter_instance, filters.BooleanFilter):
            return openapi.TYPE_BOOLEAN

        if isinstance(filter_instance, filters.DateFilter):
            return openapi.TYPE_STRING

        if isinstance(filter_instance, filters.DateTimeFilter):
            return openapi.TYPE_STRING

        if isinstance(filter_instance, filters.BaseInFilter):
            return openapi.TYPE_STRING

        return openapi.TYPE_STRING

    def get_filter_format(self, filter_instance):
        if isinstance(filter_instance, filters.DateFilter):
            return openapi.FORMAT_DATE

        if isinstance(filter_instance, filters.DateTimeFilter):
            return openapi.FORMAT_DATETIME

        return None
