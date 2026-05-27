from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SendOTPView, VerifyOTPView, SetPasswordView, LoginView, \
    PasswordResetSendView, PasswordResetVerifyView, PasswordResetConfirmView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/set/', SetPasswordView.as_view(), name='set_password'),
    path('login/', LoginView.as_view(), name='login'),
    path('password/reset/send/', PasswordResetSendView.as_view(), name='password-reset-send'),
    path('password/reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
