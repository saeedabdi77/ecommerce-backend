from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.

class TestView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        return Response({'message': 'test', 'data': 'test test testtt'}, status=status.HTTP_200_OK)
