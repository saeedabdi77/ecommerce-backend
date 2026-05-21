import datetime
import decimal
import uuid
from types import NoneType

from django.forms import model_to_dict

from middlewares.middlewares import RequestMiddleware


class BaseSignalLog:
    def __init__(self, log_model, *args, **kwargs):
        self.log_model = log_model
        self.update_action = 'UPDATE'
        self.create_action = 'CREATE'
        self.delete_action = 'DELETE'
        self.m2m_update_action = 'M2M_UPDATE'

    @staticmethod
    def _get_user():
        try:
            request = RequestMiddleware(get_response=None)
            request = request.thread_local.current_request
        except:
            request = None
        user = None
        if request:
            user = request.user
            if user.is_anonymous:
                user = None
        return user

    def _save_log(self, instance, before, after, action):
        before, after = self._manage_data(before, after)
        request_user = self._get_user()
        if after or before:
            self.log_model.objects.create(content_object=instance, request_user=request_user, before=before,
                                          after=after, action=action)

    @staticmethod
    def _make_json_serializable(value):
        if type(value) is decimal.Decimal:
            return float(value)
        elif type(value) in [uuid.UUID, datetime.datetime, datetime.date, datetime.time]:
            return str(value)
        elif type(value) is NoneType:
            value = ''
            return value
        else:
            return value

    @staticmethod
    def _get_many_to_many_fields(obj, json):
        from django.db import models
        model = obj.__class__
        many_to_many_fields = [f.name for f in model._meta.get_fields() if isinstance(f, models.ManyToManyField)]
        for field in many_to_many_fields:
            json[field] = [f.id for f in getattr(obj, field).all()]
        return json

    def _manage_data(self, before, after):
        for key, value in before.items():
            before[key] = self._make_json_serializable(value)
        for key, value in after.items():
            after[key] = self._make_json_serializable(value)

        if before and after:
            for key, value in before.items():
                if value == after[key]:
                    after.pop(key)
                    before.pop(key)

        return before, after

    def update(self, instance):
        action = self.update_action
        before = {}
        after = {}

        current = instance
        current_dict = model_to_dict(current)
        if current.pk:
            previous = instance.__class__.objects.get(pk=current.pk)
            for key, value in model_to_dict(previous).items():
                if current_dict[key] != value:
                    before[key] = value
                    after[key] = current_dict[key]

            self._save_log(instance, before, after, action)

    def create(self, instance):
        action = self.create_action
        before = {}

        after = model_to_dict(instance)
        self._save_log(instance, before, after, action)

    def delete(self, instance):
        action = self.delete_action

        after = {}
        before = model_to_dict(instance)
        before = self._get_many_to_many_fields(instance, before)
        self._save_log(instance, before, after, action)

    def m2m_update(self, instance, m2m, signal_action, pk_set):
        action = self.m2m_update_action
        before = {}
        after = {}
        if signal_action == 'post_add':
            after_list = [f.id for f in getattr(instance, m2m).all()]
            after[m2m] = after_list
            before_list = after_list.copy()
            for x in pk_set:
                before_list.remove(x)
            before[m2m] = before_list

        elif signal_action == 'post_remove':
            after_list = [f.id for f in getattr(instance, m2m).all()]
            after[m2m] = after_list
            before_list = after_list.copy()
            for x in pk_set:
                before_list.append(x)
            before[m2m] = before_list
        elif signal_action == 'pre_clear':
            before_list = [f.id for f in getattr(instance, m2m).all()]
            before[m2m] = before_list
        self._save_log(instance, before, after, action)
