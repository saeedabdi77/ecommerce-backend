from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import Http404

from core.base_views import CustomRetrieveAPIView
from order.serializers import OrderRetrieveSerializer
from order.utilities import resolve_draft_order


class CartRetrieveView(CustomRetrieveAPIView):
    serializer_class = OrderRetrieveSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='guest_uid',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        guest_uid = self.request.query_params.get('guest_uid')
        user = self.request.user

        draft_order = resolve_draft_order(user, guest_uid)
        if draft_order:
            return draft_order
        raise Http404
