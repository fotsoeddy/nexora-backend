from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ai_engine.models import AICoverLetter, AISalaryEstimate, AIUsageLog

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    AI_PROVIDER="local",
)
class AIFeatureAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="candidate@example.com",
            password="StrongPass123!",
            is_email_verified=True,
            first_name="Eddy",
        )
        self.client.force_authenticate(self.user)

    def test_cover_letter_salary_and_chat(self):
        cover_letter_response = self.client.post(
            reverse("ai-cover-letter-generate"),
            {
                "job_title": "Product Designer",
                "company_name": "NeuralStream",
                "tone": "professional",
            },
            format="json",
        )
        self.assertEqual(cover_letter_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Product Designer", cover_letter_response.data["generated_text"])
        self.assertTrue(AICoverLetter.objects.filter(model_version="gpt-4.1-mini").exists())

        salary_response = self.client.post(
            reverse("ai-salary-estimate-create"),
            {"job_title": "Data Engineer", "city": "Douala", "experience_level": "3-5"},
            format="json",
        )
        self.assertEqual(salary_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("estimated_median", salary_response.data)
        self.assertTrue(AISalaryEstimate.objects.filter(model_version="gpt-4.1-mini").exists())

        chat_session_response = self.client.post(reverse("ai-chat-session-list"), {}, format="json")
        self.assertEqual(chat_session_response.status_code, status.HTTP_201_CREATED)
        session_id = chat_session_response.data["id"]

        chat_message_response = self.client.post(
            reverse("ai-chat-message-create", kwargs={"id": session_id}),
            {"content": "Give me salary advice"},
            format="json",
        )
        self.assertEqual(chat_message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(chat_message_response.data["role"], "ai")
        self.assertEqual(AIUsageLog.objects.filter(feature__in=["chat", "cover_letter", "salary"]).count(), 3)
