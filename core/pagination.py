from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination, _positive_int

from core.api_exceptions import BaseCustomException


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    default_page_size = 20

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            err_obj = BaseCustomException()
            size = request.query_params[self.page_size_query_param]
            if int(size) > self.max_page_size:
                err_obj.append_errors({
                    "message": "Page size exceeds maximum",
                    "reason": "page_size",
                })
                raise ValidationError({'message': 'Invalid inputs', 'details': err_obj.errors})

            return _positive_int(
                request.query_params[self.page_size_query_param],
                strict=True,
                cutoff=self.max_page_size
            )

        return self.default_page_size
