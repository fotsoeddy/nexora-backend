from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import CompanyProfile, JobDomain, JobOffer

User = get_user_model()


class JobOfferAPITests(APITestCase):
    def setUp(self):
        self.domain = JobDomain.objects.create(name="Engineering", slug="engineering")

        self.employer_user = User.objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        self.company = CompanyProfile.objects.create(
            user=self.employer_user,
            company_name="TechFlow Systems",
        )

        self.job_offer = JobOffer.objects.create(
            company=self.company,
            domain=self.domain,
            title="Backend Engineer",
            slug="backend-engineer-seed",
            description="Build reliable APIs.",
            city="Douala",
            country="Cameroun",
        )

    def test_list_jobs_is_public(self):
        response = self.client.get(reverse("ai-jobs-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.job_offer.uuid))
        self.assertEqual(response.data[0]["company_name"], "TechFlow Systems")

    def test_retrieve_job_returns_expected_payload(self):
        response = self.client.get(reverse("ai-jobs-detail", kwargs={"id": self.job_offer.uuid}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Backend Engineer")
        self.assertEqual(response.data["employment_type"], self.job_offer.contract_type)
        self.assertEqual(response.data["location"], "Douala, Cameroun")

    def test_company_user_can_create_job(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            reverse("ai-jobs-list"),
            {
                "title": "Frontend Engineer",
                "description": "Build modern mobile interfaces.",
                "city": "Yaounde",
                "country": "Cameroun",
                "contract_type": "CDI",
                "domain_id": str(self.domain.uuid),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = JobOffer.objects.get(title="Frontend Engineer")
        self.assertEqual(created.company, self.company)
        self.assertEqual(created.domain, self.domain)

    def test_non_company_user_cannot_create_job(self):
        user = User.objects.create_user(
            email="candidate@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse("ai-jobs-list"),
            {
                "title": "Data Analyst",
                "description": "Analyze data.",
                "city": "Douala",
                "contract_type": "CDD",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_owner_can_soft_delete_job(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.delete(reverse("ai-jobs-detail", kwargs={"id": self.job_offer.uuid}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.job_offer.refresh_from_db()
        self.assertFalse(self.job_offer.is_active)
