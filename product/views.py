from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from  datetime import datetime


# Create your views here.

class TestView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        return Response({'message': 'test', 'data': f'test api {str(datetime.now())}'}, status=status.HTTP_200_OK)
