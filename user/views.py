from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from core.base_views import CustomCreateAPIView, CustomRetrieveAPIView, CustomCreateGetUpdateViewSet
from .serializers import SendOTPSerializer, VerifyOTPSerializer, SetPasswordSerializer, LoginSerializer, \
    PasswordResetSendSerializer, PasswordResetVerifySerializer, PasswordResetConfirmSerializer, GetProfileSerializer, \
    PostProfileSerializer, PutProfileSerializer


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


class ProfileViewSet(CustomCreateGetUpdateViewSet):
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
