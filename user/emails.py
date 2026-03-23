from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner


VERIFICATION_SALT = "user-email-verification"


def build_email_verification_token(user) -> str:
    signer = TimestampSigner(salt=VERIFICATION_SALT)
    return signer.sign(str(user.pk))


def send_verification_email(user) -> str:
    token = build_email_verification_token(user)
    verify_url = f"{settings.FRONTEND_VERIFY_URL}?token={token}"
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
