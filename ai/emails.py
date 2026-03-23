from django.conf import settings
from django.core.mail import send_mail


def send_application_confirmation_email(application) -> None:
    send_mail(
        subject="Your Nexora application was received",
        message=(
            f"Hello {application.user.first_name or application.user.username},\n\n"
            f"Your application for {application.job.title} at {application.job.company_name or 'the company'} has been received.\n"
            "You can track its progress directly in the Nexora mobile app.\n\n"
            "Thank you,\n"
            "Nexora"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.user.email],
        fail_silently=False,
    )
