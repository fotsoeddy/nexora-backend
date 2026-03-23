from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ai_engine.models import AIInterviewSession, AIUsageLog
from jobs.models import CandidateProfile, CompanyProfile, JobOffer

User = get_user_model()


@override_settings(AI_PROVIDER="local")
class InterviewSessionAPITests(APITestCase):
    def setUp(self):
        self.candidate_user = User.objects.create_user(
            email="candidate@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        self.candidate_profile = CandidateProfile.objects.create(user=self.candidate_user)

        employer_user = User.objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        company = CompanyProfile.objects.create(user=employer_user, company_name="TechFlow Systems")
        self.job_offer = JobOffer.objects.create(
            company=company,
            title="Product Designer",
            slug="product-designer-seed",
            description="Design product experiences.",
            city="Douala",
            country="Cameroun",
        )

    def test_authenticated_user_can_create_and_list_sessions(self):
        self.client.force_authenticate(self.candidate_user)

        create_response = self.client.post(
            reverse("ai-interview-session-list"),
            {"job_offer_id": str(self.job_offer.uuid), "difficulty": "easy"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_response = self.client.get(reverse("ai-interview-session-list"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["job_title"], "Product Designer")

    def test_generate_endpoint_creates_questions(self):
        self.client.force_authenticate(self.candidate_user)

        response = self.client.post(
            reverse("ai-interview-session-generate"),
            {
                "custom_job_title": "Backend Engineer",
                "difficulty": "medium",
                "questions_count": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["questions_count"], 3)
        self.assertEqual(len(response.data["messages"]), 3)
        self.assertEqual(response.data["messages"][0]["role"], "ai")
        self.assertEqual(AIUsageLog.objects.filter(feature="interview_generation").count(), 1)

    def test_submit_answer_updates_session_and_scores_response(self):
        self.client.force_authenticate(self.candidate_user)
        session_response = self.client.post(
            reverse("ai-interview-session-generate"),
            {
                "custom_job_title": "Backend Engineer",
                "difficulty": "medium",
                "questions_count": 2,
            },
            format="json",
        )
        session_id = session_response.data["id"]

        answer_response = self.client.post(
            reverse("ai-interview-answer-submit", kwargs={"id": session_id}),
            {
                "content": "I led a backend redesign that reduced latency by 35% and improved team delivery.",
            },
            format="json",
        )
        self.assertEqual(answer_response.status_code, status.HTTP_200_OK)
        user_messages = [message for message in answer_response.data["messages"] if message["role"] == "user"]
        self.assertEqual(len(user_messages), 1)
        self.assertIsNotNone(user_messages[0]["answer_score"])
        self.assertTrue(user_messages[0]["answer_feedback"])

        final_answer_response = self.client.post(
            reverse("ai-interview-answer-submit", kwargs={"id": session_id}),
            {
                "content": "In my first 90 days I would improve observability, align the roadmap, and ship measurable wins.",
            },
            format="json",
        )
        self.assertEqual(final_answer_response.status_code, status.HTTP_200_OK)
        self.assertEqual(final_answer_response.data["status"], "completed")
        self.assertIsNotNone(final_answer_response.data["overall_score"])
        self.assertTrue(final_answer_response.data["strengths_noted"])
        self.assertEqual(AIUsageLog.objects.filter(feature="interview_evaluation").count(), 2)

    def test_user_can_only_retrieve_own_session(self):
        session = AIInterviewSession.objects.create(
            candidate=self.candidate_profile,
            custom_job_title="Backend Engineer",
        )

        other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            is_email_verified=True,
        )
        CandidateProfile.objects.create(user=other_user)

        self.client.force_authenticate(other_user)
        response = self.client.get(reverse("ai-interview-session-detail", kwargs={"id": session.uuid}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
