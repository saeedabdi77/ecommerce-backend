import random
import re
from datetime import datetime, timedelta

from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from core.base_serializers import CustomSerializer
from user.models import User

from decouple import config

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

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')

        otp_code = str(random.randint(1000, 9999))

        cache.set(f"otp_{phone_number}", otp_code, timeout=120)

        # TODO: Implement actual SMS provider sending logic here
        print(f"\n[SMS LOG] OTP for {phone_number}: {otp_code}\n")
        return validated_data


class VerifyOTPSerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=4, min_length=4, write_only=True)

    def validate_serializer(self, attrs, error_obj):
        phone_number = attrs.get('phone_number')
        otp_received = attrs.get('otp')

        master_otp = config('MASTER_OTP_CODE')
        cached_otp = cache.get(f"otp_{phone_number}")

        if not ((master_otp and otp_received == str(master_otp)) or (otp_received == cached_otp)):
            error_obj.append_errors({
                "message": "کد تایید نادرست است",
                "reason": "otp"
            })
        return attrs

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)

        refresh = RefreshToken.for_user(user)
        validated_data['access'] = str(refresh.access_token)
        validated_data['refresh'] = str(refresh)
        validated_data['is_new_user'] = str(created)

        return validated_data


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


class PasswordResetSendSerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)

    def validate_serializer(self, attrs, error_obj):
        phone_number = attrs.get('phone_number')

        # Regex for Iranian mobile format: starts with 09 and 11 digits total
        if not re.match(r'^09\d{9}$', phone_number):
            error_obj.append_errors({
                "message": "فرمت شماره موبایل نامعتبر است. مثال: 09123456789",
                "reason": "phone_number"
            })

        try:
            user = User.objects.get(username=phone_number)
            attrs.set('user', user)
        except User.DoesNotExist:
            error_obj.append_errors({
                "message": "کاربری با این شماره پیدا نشد",
                "reason": "phone_number"
            })
        return attrs

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        otp_code = str(random.randint(1000, 9999))
        cache.set(f"reset_otp_{phone_number}", otp_code, timeout=120)

        # TODO: Implement actual SMS provider sending logic here
        print(f"\n[SMS LOG] OTP for {phone_number}: {otp_code}\n")
        return validated_data


class PasswordResetVerifySerializer(CustomSerializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)
    otp = serializers.CharField(max_length=4, min_length=4, write_only=True)

    def validate_serializer(self, attrs, error_obj):
        phone_number = attrs.get('phone_number')
        otp_received = attrs.get('otp')

        master_otp = config('MASTER_OTP_CODE')
        cached_otp = cache.get(f"reset_otp_{phone_number}")

        if not ((master_otp and otp_received == str(master_otp)) or (otp_received == cached_otp)):
            error_obj.append_errors({
                "message": "کد تایید نادرست است",
                "reason": "otp"
            })
        return attrs

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')

        payload = {
            'phone_number': phone_number,
            'exp': datetime.now() + timedelta(minutes=10),
            'purpose': 'password_reset'
        }

        reset_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        validated_data["reset_token"] = reset_token
        return validated_data


class PasswordResetConfirmSerializer(CustomSerializer):
    reset_token = serializers.CharField()
    phone_number = serializers.CharField(max_length=11, min_length=11)
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)

    def validate_serializer(self, attrs, error_obj):
        reset_token = attrs.get('reset_token')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        repeat_password = attrs.get('repeat_password')

        payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=['HS256'])
        payload_purpose = payload.get('purpose')
        payload_phone_number = payload.get('phone_number')
        payload_exp = payload.get('exp')

        if payload_purpose != 'password_reset' or payload_phone_number != phone_number or payload_exp < datetime.now():
            error_obj.append_errors({
                "message": "عملیات ناموفق",
                "reason": "reset_token"
            })

        if password != repeat_password:
            error_obj.append_errors({
                "message": "پسوورد مطابقت ندارد",
                "reason": "repeat_password"
            })
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        user = self.request.user

        user.set_password(password)
        user.save()
        return validated_data
