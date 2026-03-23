from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import CompanyProfile, JobOffer

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class CandidateFeatureAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="candidate@example.com",
            password="StrongPass123!",
            is_email_verified=True,
            first_name="Eddy",
        )
        employer = User.objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        company = CompanyProfile.objects.create(user=employer, company_name="TechFlow Systems")
        self.job_offer = JobOffer.objects.create(
            company=company,
            title="Data Engineer",
            slug="data-engineer-seed",
            description="Build pipelines.",
            city="Douala",
            country="Cameroun",
        )
        self.client.force_authenticate(self.user)

    def test_saved_jobs_flow(self):
        create_response = self.client.post(
            reverse("saved-jobs-list"),
            {"job_offer_id": str(self.job_offer.uuid)},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_response = self.client.get(reverse("saved-jobs-list"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        delete_response = self.client.delete(reverse("saved-jobs-destroy", kwargs={"job_id": self.job_offer.uuid}))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        recreate_response = self.client.post(
            reverse("saved-jobs-list"),
            {"job_offer_id": str(self.job_offer.uuid)},
            format="json",
        )
        self.assertEqual(recreate_response.status_code, status.HTTP_201_CREATED)

    def test_applications_and_alerts_flow(self):
        application_response = self.client.post(
            reverse("applications-list"),
            {"job_offer_id": str(self.job_offer.uuid)},
            format="json",
        )
        self.assertEqual(application_response.status_code, status.HTTP_201_CREATED)

        alert_response = self.client.post(
            reverse("job-alerts-list"),
            {
                "name": "Data roles",
                "keywords": "Data",
                "cities": ["Douala"],
                "contract_types": ["CDI"],
                "frequency": "daily",
            },
            format="json",
        )
        self.assertEqual(alert_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(alert_response.data["frequency"], "daily")
