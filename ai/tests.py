from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ai.models import (
    Application,
    AssistantChatSession,
    CoverLetterDraft,
    InterviewAnswer,
    InterviewFeedback,
    InterviewQuestion,
    InterviewSession,
    Job,
    JobAlert,
    SalaryEstimate,
    SavedJob,
)

User = get_user_model()


@override_settings(
    VAPI_WEBHOOK_TOKEN="test-token",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    OPENAI_API_KEY="",
)
class InterviewWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password="StrongPass123!",
        )
        self.job = Job.objects.create(
            title="Backend Engineer",
            company_name="TechFlow",
            description="Build backend services",
            requirements="Python, Django, APIs",
            location="Douala",
        )
        self.client.force_authenticate(self.user)

    def test_generate_session_and_submit_answer(self):
        generate_response = self.client.post(
            reverse("job-interview-generate"),
            {"job_id": str(self.job.id), "question_count": 2, "interview_type": "mixed"},
            format="json",
        )
        self.assertEqual(generate_response.status_code, status.HTTP_201_CREATED)
        session_id = generate_response.data["id"]
        session = InterviewSession.objects.get(pk=session_id)
        first_question = session.questions.order_by("order").first()

        answer_response = self.client.post(
            reverse("interview-answer-submit", kwargs={"pk": session_id}),
            {
                "question_id": str(first_question.id),
                "answer_text": "I redesigned an API and reduced latency by 35% while coordinating the rollout with the team.",
            },
            format="json",
        )
        self.assertEqual(answer_response.status_code, status.HTTP_200_OK)
        self.assertEqual(InterviewAnswer.objects.filter(session=session).count(), 1)
        self.assertIn("latest_answer_evaluation", answer_response.data)

    def test_vapi_save_answer_persists_record(self):
        session = InterviewSession.objects.create(
            user=self.user,
            job=self.job,
            session_type="job_based",
            interview_status="questions_generated",
            interview_type="mixed",
            question_count=1,
        )
        question = InterviewQuestion.objects.create(
            session=session,
            order=1,
            question_text="What makes you a fit for this role?",
            question_type="mixed",
        )

        response = self.client.post(
            reverse("vapi-save-answer"),
            {
                "message": {
                    "toolCallList": [
                        {
                            "toolCallId": "call_1",
                            "function": {
                                "arguments": {
                                    "sessionId": str(session.id),
                                    "questionId": str(question.id),
                                    "answer": "I build reliable APIs and improve delivery quality.",
                                }
                            },
                        }
                    ]
                }
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer test-token",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(InterviewAnswer.objects.filter(session=session, question=question).count(), 1)

    def test_finalize_feedback_creates_feedback_record(self):
        session = InterviewSession.objects.create(
            user=self.user,
            job=self.job,
            session_type="job_based",
            interview_status="in_progress",
            interview_type="mixed",
            question_count=1,
        )
        question = InterviewQuestion.objects.create(
            session=session,
            order=1,
            question_text="Describe a backend challenge you solved.",
            question_type="technical",
        )
        InterviewAnswer.objects.create(
            session=session,
            question=question,
            answer_text="I migrated a service and reduced errors by 20%.",
        )

        response = self.client.post(
            reverse("vapi-grade-interview"),
            {
                "message": {
                    "toolCallList": [
                        {
                            "toolCallId": "call_2",
                            "function": {
                                "arguments": {
                                    "sessionId": str(session.id),
                                }
                            },
                        }
                    ]
                }
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer test-token",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(InterviewFeedback.objects.filter(session=session).exists())

    def test_application_saved_jobs_and_alerts_workflow(self):
        saved_response = self.client.post(
            reverse("saved-job-list-create"),
            {"job_offer_id": str(self.job.id)},
            format="json",
        )
        self.assertEqual(saved_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavedJob.objects.filter(user=self.user, job=self.job).count(), 1)

        application_response = self.client.post(
            reverse("application-list-create"),
            {"job_offer_id": str(self.job.id), "cover_letter": "I build reliable APIs."},
            format="json",
        )
        self.assertEqual(application_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.filter(user=self.user, job=self.job).count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        alert_response = self.client.post(
            reverse("job-alert-list-create"),
            {
                "name": "Backend roles",
                "keywords": "Backend",
                "cities": ["Douala"],
                "contract_types": [],
                "frequency": "daily",
                "notify_by_email": True,
                "notify_by_push": False,
            },
            format="json",
        )
        self.assertEqual(alert_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobAlert.objects.filter(user=self.user).count(), 1)

        list_response = self.client.get(reverse("job-alert-list-create"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data[0]["matches"], 1)

    def test_chat_cover_letter_and_salary_endpoints(self):
        chat_response = self.client.post(
            reverse("chat-session-list-create"),
            {"title": "Career assistant", "context_type": "career_advice"},
            format="json",
        )
        self.assertEqual(chat_response.status_code, status.HTTP_201_CREATED)
        session_id = chat_response.data["id"]
        self.assertTrue(AssistantChatSession.objects.filter(user=self.user, pk=session_id).exists())

        message_response = self.client.post(
            reverse("chat-message-create", kwargs={"id": session_id}),
            {"content": "How can I improve my CV?"},
            format="json",
        )
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("content", message_response.data)

        cover_letter_response = self.client.post(
            reverse("cover-letter-generate"),
            {"job_title": "Backend Engineer", "company_name": "TechFlow", "tone": "professional"},
            format="json",
        )
        self.assertEqual(cover_letter_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CoverLetterDraft.objects.filter(user=self.user).count(), 1)

        salary_response = self.client.post(
            reverse("salary-estimate-create"),
            {"job_title": "Backend Engineer", "city": "Douala", "experience_level": "3-5"},
            format="json",
        )
        self.assertEqual(salary_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SalaryEstimate.objects.filter(user=self.user).count(), 1)
