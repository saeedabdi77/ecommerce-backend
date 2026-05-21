from collections import OrderedDict

from django_rest.http.exceptions import InternalServerError
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.fields import get_error_detail, SkipField, set_value, ListField, empty, CharField
from rest_framework.serializers import as_serializer_error
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjangoValidationError
from sentry_sdk import capture_message


class CustomSerializer(serializers.Serializer):

    def set_errors(self, errors=None):
        if errors is None:
            errors = []
        self.error_list = errors

    def is_valid(self, *, raise_exception=False):
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )
        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = []
                self._errors = exc.detail
            else:
                self._errors = []
        if self._errors and raise_exception:
            try:
                error_z = self.error_list
            except Exception as e:
                capture_message(f'CustomSerializer error capture:\n{e}')  # Sentry event
                raise APIException(
                    {'message': _('Internal Server Error! backend: Ozrkhahi pishapish :)'), 'details': self.errors, 'Exception': e})
            if error_z:
                raise ValidationError(
                    {'message': _('Invalid inputs'), 'details': error_z})

        return not bool(self._errors)

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        error_obj = BaseCustomException()
        value, errors = self.to_internal_value(data)

        for error, detail in dict(errors).items():
            error_obj.append_errors({
                "message": _(detail[0]),
                "reason": error
            })

        try:
            # self.run_validators(value)
            value = self.validate(value, error_obj)

            assert value is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=as_serializer_error(exc))

        return value

    def validate(self, attrs, error_obj=None):
        self.validate_serializer(attrs, error_obj)
        if len(error_obj.get_errors()) > 0:
            self.set_errors(error_obj.get_errors())
            raise error_obj

        return attrs

    def validate_serializer(self, attrs, error_obj):
        return attrs

    def to_internal_value(self, data):
        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            if isinstance(field, ListField) and primitive_value != empty and len(primitive_value) == 1 and isinstance(
                    primitive_value[0], str):
                primitive_value = primitive_value[0].split(',')

            try:
                if isinstance(field, CharField) and isinstance(primitive_value, str) and field.max_length and len(
                        primitive_value) > field.max_length:
                    raise ValidationError(_(f'{field.field_name} must be less than or equal to {field.max_length}'))

                if field.required and primitive_value == '':
                    primitive_value = empty
                field.validate_empty_values(primitive_value)
                validated_value = field.to_internal_value(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        return ret, errors

    def create(self, validated_data):
        try:
            self.create_serializer(validated_data)
        except Exception as e:
            raise APIException({'message': APIException.default_detail, 'error': e})

    def update(self, instance, validated_data):
        try:
            self.update_serializer(instance, validated_data)
        except Exception as e:
            raise APIException({'message': APIException.default_detail, 'error': e})

    def create_serializer(self, validated_data):
        raise NotImplementedError('`create_serializer()` must be implemented.')

    def update_serializer(self, instance, validated_data):
        raise NotImplementedError('`update_serializer()` must be implemented.')


class CustomModelSerializer(serializers.ModelSerializer, CustomSerializer):
    pass


class BaseCustomException(ValidationError):
    errors = []

    def __init__(self, errors=None):
        if errors is None:
            errors = []
        self.errors = errors
        super().__init__('')  # Set detail to an empty string initially

    def get_errors(self):
        return self.errors

    def append_errors(self, error):
        self.errors.append(error)
