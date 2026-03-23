from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


def send_application_confirmation_email(application) -> None:
    candidate_email = application.candidate.user.email
    job_title = application.job_offer.title

    send_mail(
        subject=f"Application received for {job_title}",
        message=(
            "Your application has been recorded successfully.\n\n"
            f"Job: {job_title}\n"
            f"Company: {application.job_offer.company.company_name}\n"
            f"Status: {application.status}\n\n"
            "You can track future updates from your Nexora application dashboard."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[candidate_email],
        fail_silently=False,
    )
