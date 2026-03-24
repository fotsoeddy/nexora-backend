from django.urls import path
from user.api.views.auth import (
    CustomTokenObtainPairView,
    MeView,
    RefreshView,
    RegisterView,
    ResendVerificationEmailView,
    UserSerializer,
    VerifyEmailConfirmView,
    UserConfigView,
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login', CustomTokenObtainPairView.as_view()),
    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),
    path('token/refresh', RefreshView.as_view()),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/login', CustomTokenObtainPairView.as_view()),
    path('auth/refresh/', RefreshView.as_view(), name='auth-refresh'),
    path('auth/refresh', RefreshView.as_view()),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/register', RegisterView.as_view()),
    path('auth/email/resend/', ResendVerificationEmailView.as_view(), name='auth-email-resend'),
    path('auth/email/resend', ResendVerificationEmailView.as_view()),
    path('auth/email/verify/confirm/', VerifyEmailConfirmView.as_view(), name='auth-email-verify-confirm'),
    path('auth/email/verify/confirm', VerifyEmailConfirmView.as_view()),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/me', MeView.as_view()),
    path('auth/config/', UserConfigView.as_view(), name='user-config'),
    path('auth/config', UserConfigView.as_view()),
]
