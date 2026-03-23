from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from user.api.serializers.auth import (
    CustomTokenObtainPairSerializer,
    EmailSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    RegisterResponseSerializer,
    ResendVerificationResponseSerializer,
    UserSerializer,
)
from user.emails import VERIFICATION_SALT, send_verification_email
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Authentication"],
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: OpenApiResponse(description="Invalid credentials or email not verified."),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Login request received with data: {request.data}")
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except APIException as exc:
            detail = exc.detail
            if isinstance(detail, dict):
                payload = detail
            else:
                payload = {"detail": detail}
            logger.error(f"Validation failed for login: {payload}")
            status_code = (
                status.HTTP_401_UNAUTHORIZED
                if "credential" in str(payload).lower()
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(payload, status=status_code)
        except Exception:
            logger.exception("Unexpected login error")
            return Response(
                {"detail": "Unable to sign in right now. Please retry."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info("Validation successful, returning token")
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: OpenApiResponse(description="Validation error."),
    },
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user, request=request)
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "message": "Account created. A verification email has been sent.",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Authentication"],
    request=EmailSerializer,
    responses={200: ResendVerificationResponseSerializer},
)
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.is_active:
            send_verification_email(user, request=request)
        return Response(
            {"message": "If the account exists and is not verified, a new verification email has been sent."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication"],
    parameters=[
        OpenApiParameter(
            name="token",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
            description="Signed verification token sent by email.",
        )
    ],
    responses={
        200: OpenApiResponse(description="Email successfully verified."),
        400: OpenApiResponse(description="Expired or invalid verification token."),
    },
)
class VerifyEmailConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token", "")
        signer = TimestampSigner(salt=VERIFICATION_SALT)
        try:
            user_id = signer.unsign(token, max_age=60 * 60 * 24 * 3)
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save(update_fields=["is_active"])
            return HttpResponse(
                "<h1>Email verified</h1><p>Your Nexora account is now active. You can return to the app and sign in.</p>"
            )
        except SignatureExpired:
            return HttpResponse(
                "<h1>Verification link expired</h1><p>Please request a new verification email from the app.</p>",
                status=400,
            )
        except (BadSignature, User.DoesNotExist):
            return HttpResponse(
                "<h1>Invalid verification link</h1><p>Please request a new verification email from the app.</p>",
                status=400,
            )


@extend_schema(
    tags=["Authentication"],
    responses={200: UserSerializer},
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)


@extend_schema(
    tags=["Authentication"],
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiResponse(description="Access token refreshed."),
        401: OpenApiResponse(description="Refresh token invalid or expired."),
    },
)
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    pass
