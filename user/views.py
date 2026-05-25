import random
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.base_views import CustomCreateAPIView
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from user.models import User

from decouple import config


class SendOTPView(CustomCreateAPIView):
    serializer_class = SendOTPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        otp_code = str(random.randint(1000, 9999))

        cache.set(f"otp_{phone_number}", otp_code, timeout=120)

        # TODO: Implement actual SMS provider sending logic here
        print(f"\n[SMS LOG] OTP for {phone_number}: {otp_code}\n")

        return Response({
            'message': "OTP code is sent successfully",
            'data': {"phone_number": phone_number}
        }, status=status.HTTP_200_OK)


class VerifyOTPView(CustomCreateAPIView):
    serializer_class = VerifyOTPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_received = serializer.validated_data['otp']

        master_otp = config('MASTER_OTP_CODE')
        cached_otp = cache.get(f"otp_{phone_number}")

        if (master_otp and otp_received == str(master_otp)) or (otp_received == cached_otp):
            user, created = User.objects.get_or_create(phone_number=phone_number)

            refresh = RefreshToken.for_user(user)

            return Response({
                'message': "SUCCESS",
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'is_new_user': created
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'message': "Invalid OTP",
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
