import re
from rest_framework import serializers

from core.base_serializers import CustomSerializer


class SendOTPSerializer(CustomSerializer):
    # Ensure phone number is exactly 11 digits
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
