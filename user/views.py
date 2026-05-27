from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from core.base_views import CustomCreateAPIView
from .serializers import SendOTPSerializer, VerifyOTPSerializer, SetPasswordSerializer, LoginSerializer, \
    PasswordResetSendSerializer, PasswordResetVerifySerializer



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
