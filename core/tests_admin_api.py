from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ai.models import Application, InterviewSession, Job


class AdminDashboardAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="AdminPass123!",
            is_active=True,
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="candidate@example.com",
            email="candidate@example.com",
            password="CandidatePass123!",
            is_active=True,
        )
        self.job = Job.objects.create(
            title="Backend Engineer",
            company_name="Nexora",
            description="Build APIs",
            location="Douala",
            employment_type="full_time",
            created_by=self.admin,
        )
        Application.objects.create(user=self.user, job=self.job, status="pending", ats_score=82)
        InterviewSession.objects.create(
            user=self.user,
            job=self.job,
            session_type="job_based",
            interview_type="mixed",
            interview_status="pending",
            question_count=5,
        )

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)

    def test_staff_can_read_dashboard(self):
        self.authenticate_admin()

        response = self.client.get(reverse("admin-dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["metrics"]), 4)
        self.assertTrue(any(item["label"] == "Applications" for item in response.data["metrics"]))

    def test_non_staff_cannot_read_dashboard(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("admin-dashboard"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_application_status(self):
        self.authenticate_admin()
        application = Application.objects.get()

        response = self.client.patch(
            reverse("admin-application-detail", kwargs={"pk": application.pk}),
            {"status": "reviewed", "recruiter_notes": "Profile looks strong."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, "reviewed")
        self.assertEqual(application.recruiter_notes, "Profile looks strong.")

    def test_staff_can_create_job_from_admin_endpoint(self):
        self.authenticate_admin()

        response = self.client.post(
            reverse("admin-jobs"),
            {
                "title": "Frontend Engineer",
                "company_name": "Nexora",
                "description": "Build the admin dashboard",
                "requirements": "React",
                "employment_type": "full_time",
                "location": "Remote",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Job.objects.filter(title="Frontend Engineer").exists())

    def test_staff_can_list_companies(self):
        self.authenticate_admin()

        response = self.client.get(reverse("admin-companies"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["company_name"], "Nexora")

    def test_staff_can_toggle_publication_status(self):
        self.authenticate_admin()

        response = self.client.patch(
            reverse("admin-publication-detail", kwargs={"pk": self.job.pk}),
            {"publication_status": "inactive"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 0)

    def test_staff_can_read_operations_snapshot(self):
        self.authenticate_admin()

        response = self.client.get(reverse("admin-operations"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metrics", response.data)
        self.assertIn("alerts", response.data)
