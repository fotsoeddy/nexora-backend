from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.urls import reverse
from urllib.parse import quote


VERIFICATION_SALT = "user-email-verification"


def build_email_verification_token(user) -> str:
    signer = TimestampSigner(salt=VERIFICATION_SALT)
    return signer.sign(str(user.pk))


def build_email_verification_url(token: str, request=None) -> str:
    encoded_token = quote(token, safe="")

    if request is not None:
        verify_path = reverse("auth-email-verify-confirm")
        return request.build_absolute_uri(f"{verify_path}?token={encoded_token}")

    base_url = settings.FRONTEND_VERIFY_URL.rstrip("/")
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}token={encoded_token}"


def send_verification_email(user, request=None) -> str:
    token = build_email_verification_token(user)
    verify_url = build_email_verification_url(token, request=request)
    send_mail(
        subject="Verify your Nexora account",
        message=(
            "Welcome to Nexora.\n\n"
            "Please verify your email address by opening this link:\n"
            f"{verify_url}\n\n"
            "If you did not create this account, you can ignore this message."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return token
