import re
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from core.base_serializers import CustomSerializer
from user.models import User


class SendOTPSerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)

    def validate_serializer(self, attrs, error_obj):
        phone = attrs.get('phone_number', '')

        # Regex for Iranian mobile format: starts with 09 and 11 digits total
        if not re.match(r'^09\d{9}$', phone):
            error_obj.append_errors({
                "message": "فرمت شماره موبایل نامعتبر است. مثال: 09123456789",
                "reason": "phone_number"
            })
        return attrs


class VerifyOTPSerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=4, min_length=4)

    def validate_serializer(self, attrs, error_obj):
        return attrs


class SetPasswordSerializer(CustomSerializer):
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)

    def validate_serializer(self, attrs, error_obj):
        password = attrs.get('password')
        repeat_password = attrs.get('repeat_password')
        user = self.request.user

        if password != repeat_password:
            error_obj.append_errors({
                "message": "پسوورد مطابقت ندارد",
                "reason": "repeat_password"
            })
        if user.password is not None:
            error_obj.append_errors({
                "message": "پسوورد تعیین شده است",
                "reason": "repeat_password"
            })
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        user = self.request.user

        user.set_password(password)
        user.save()
        return validated_data


class LoginSerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)
    password = serializers.CharField(write_only=True)

    def validate_serializer(self, attrs, error_obj):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.check_password(password):
                error_obj.append_errors({
                    "message": "شماره موبایل یا رمز عبور نادرست است",
                    "reason": "password"
                })
        except User.DoesNotExist:
            error_obj.append_errors({
                "message": "شماره موبایل یا رمز عبور نادرست است",
                "reason": "password"
            })
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        refresh = RefreshToken.for_user(user)
        validated_data['access'] = str(refresh.access_token)
        validated_data['refresh'] = str(refresh)
        return validated_data
