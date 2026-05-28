from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet, ViewSetMixin
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination


class CustomCreateModelMixin:
    """
    Create a model instance.
    """

    def create(self, request, message="Instance created successfully", status_code=status.HTTP_201_CREATED, *args,
               **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': message, 'data': serializer.data},
                        status=status_code, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class CustomUpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, message="Instance updated successfully", status_code=status.HTTP_200_OK, *args,
               **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({'message': message, 'data': serializer.data}, status=status_code)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class CustomRetrieveModelMixin:
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, message="Instance retrieved successfully", status_code=status.HTTP_200_OK, *args,
                 **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'message': message, 'data': serializer.data}, status=status_code)


class CustomDestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, message="Instance deleted successfully", status_code=status.HTTP_204_NO_CONTENT,
                *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': message}, status=status_code)

    def perform_destroy(self, instance):
        instance.delete()

    def perform_dige_vaqan_destroy(self, instance):
        instance.force_delete()

    def force_destroy(self, request, message="Instance deleted successfully", status_code=status.HTTP_204_NO_CONTENT,
                      *args, **kwargs):
        instance = self.get_object()
        self.perform_dige_vaqan_destroy(instance)
        return Response({'message': message}, status=status_code)

    def delete(self, request, message="Instance delete successfully", status_code=status.HTTP_204_NO_CONTENT,
               *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(instance)
        return Response({'message': message}, status=status_code)


class CustomListModelMixin:
    """
    List a queryset.
    """

    sorts_items = ()

    def list(self, request, message="Instances listed successfully", status_code=status.HTTP_200_OK, *args,
             **kwargs):

        queryset_all = self.get_queryset()
        queryset = self.filter_queryset(queryset_all)
        queryset = self.optimize_query(queryset)
        queryset = self.sort_queryset(queryset, request)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data

            return Response({'message': message, 'data': data}, status=status_code)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response({'message': message, 'data': {'result': serializer.data}}, status=status_code)

    def sort_queryset(self, queryset, request):
        sort_item = self.get_sort_item(request)
        sort_option_keys = self.get_sort_option_keys()

        if sort_item is not None and sort_item in sort_option_keys:
            sort_value = self.get_sort_value(sort_item)
            sorted_queryset = queryset.order_by(sort_value)
            return sorted_queryset
        return queryset

    def optimize_query(self, queryset):
        return queryset

    @staticmethod
    def get_sort_item(request):
        return request.query_params.get('sort_by', None)

    def get_sort_option_keys(self):
        return list(map(lambda x: x[0], self.sorts_items))

    def get_sort_value(self, key):
        for sort in self.sorts_items:
            if sort[0] == key:
                return sort[1]


class CustomRetrieveAPIView(CustomRetrieveModelMixin, GenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CustomCreateAPIView(CustomCreateModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomListAPIView(CustomListModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CustomUpdateAPIView(CustomUpdateModelMixin, GenericAPIView):
    """
        Concrete view for updating a model instance.
        """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CustomDestroyAPIView(CustomDestroyModelMixin, GenericAPIView):
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomGenericViewSet(ViewSetMixin, GenericAPIView):
    """
    permissions code_name are added to view
    """
    pass


class CustomCreateGetUpdateDestroyViewSet(CustomCreateModelMixin,
                                          CustomUpdateModelMixin,
                                          CustomRetrieveAPIView,
                                          CustomDestroyAPIView,
                                          GenericViewSet):
    pass


class CustomCreateGetUpdateViewSet(CustomCreateModelMixin,
                                   CustomUpdateModelMixin,
                                   CustomRetrieveAPIView,
                                   GenericViewSet):
    pass
