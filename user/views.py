from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from core.base_views import CustomCreateAPIView, CustomCreateRetrieveUpdateViewSet, \
    CustomCreateListUpdateDestroyViewSet, CustomListAPIView
from .models import Address, Province, City
from .serializers import SendOTPSerializer, VerifyOTPSerializer, SetPasswordSerializer, LoginSerializer, \
    PasswordResetSendSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer, GetProfileSerializer, \
    CreateProfileSerializer, UpdateProfileSerializer, GetAddressSerializer, CreateAddressSerializer, \
    UpdateAddressSerializer, ProvinceSerializer, CitySerializer


class SendOTPView(CustomCreateAPIView):
    serializer_class = SendOTPSerializer


class VerifyOTPView(CustomCreateAPIView):
    serializer_class = VerifyOTPSerializer


class SetPasswordView(CustomCreateAPIView):
    serializer_class = SetPasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class LoginView(CustomCreateAPIView):
    serializer_class = LoginSerializer


class PasswordResetSendView(CustomCreateAPIView):
    serializer_class = PasswordResetSendSerializer


class PasswordResetVerifyView(CustomCreateAPIView):
    serializer_class = PasswordResetVerifySerializer


class PasswordResetConfirmView(CustomCreateAPIView):
    serializer_class = PasswordResetConfirmSerializer


class ProfileViewSet(CustomCreateRetrieveUpdateViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'put', 'get']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProfileSerializer
        elif self.request.method == 'PUT':
            return UpdateProfileSerializer
        else:
            return GetProfileSerializer


class AddressViewSet(CustomCreateListUpdateDestroyViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'put', 'get', 'delete']
    lookup_field = 'id'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_object(self):
        address_id = self.kwargs['id']
        user = self.request.user
        return get_object_or_404(Address, id=address_id, user=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAddressSerializer
        elif self.request.method == 'PUT':
            return UpdateAddressSerializer
        else:
            return GetAddressSerializer


class ProvinceView(CustomListAPIView):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all()
    pagination_class = None


class CityView(CustomListAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    lookup_field = 'province__id'
    pagination_class = None
