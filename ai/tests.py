from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ai.models import InterviewAnswer, InterviewFeedback, InterviewQuestion, InterviewSession, Job

User = get_user_model()


@override_settings(VAPI_WEBHOOK_TOKEN="test-token")
class InterviewWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate", password="StrongPass123!")
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
        session_id = generate_response.data["session_id"]
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
