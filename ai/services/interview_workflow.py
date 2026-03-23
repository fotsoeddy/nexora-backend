from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from ai.models import InterviewAnswer, InterviewFeedback, InterviewQuestion, InterviewSession
from ai.openai_utils import evaluate_interview_answer, grade_interview_openai
from global_data.enum import InterviewStatus


def save_interview_answer(
    *,
    session: InterviewSession,
    question: InterviewQuestion,
    answer_text: str = "",
    transcript: str = "",
    duration_seconds: int | None = None,
) -> InterviewAnswer:
    answer, _ = InterviewAnswer.objects.update_or_create(
        session=session,
        question=question,
        defaults={
            "answer_text": answer_text,
            "transcript": transcript or answer_text,
            "duration_seconds": duration_seconds,
            "answered_at": timezone.now(),
        },
    )
    if session.interview_status == InterviewStatus.QUESTIONS_GENERATED:
        session.interview_status = InterviewStatus.IN_PROGRESS
        session.started_at = session.started_at or timezone.now()
        session.save(update_fields=["interview_status", "started_at", "modified"])
    return answer


@transaction.atomic
def finalize_interview_feedback(*, session: InterviewSession) -> InterviewFeedback:
    questions = list(session.questions.order_by("order"))
    answers = {
        answer.question_id: answer
        for answer in session.answers.select_related("question").all()
    }
    payload = [
        {
            "id": str(question.id),
            "question": question.question_text,
            "answer": answers.get(question.id).answer_text if answers.get(question.id) else "",
        }
        for question in questions
    ]
    grading_result = grade_interview_openai(
        job_metadata={
            "jobTitle": session.job.title if session.job else session.target_job_title or "Interview",
            "interviewType": session.interview_type,
            "seniority": session.seniority,
        },
        questions_with_answers=payload,
    )
    feedback, _ = InterviewFeedback.objects.update_or_create(
        session=session,
        defaults={
            "overall_score": grading_result.get("overallScore"),
            "hire_readiness": grading_result.get("hireReadiness"),
            "strengths": grading_result.get("strengths", []),
            "improvements": grading_result.get("improvements", []),
            "summary_to_read_aloud": grading_result.get("summaryToReadAloud"),
            "raw_response": grading_result,
        },
    )
    session.interview_status = InterviewStatus.GRADED
    session.completed_at = session.completed_at or timezone.now()
    session.save(update_fields=["interview_status", "completed_at", "modified"])
    return feedback


def evaluate_answer_inline(*, session: InterviewSession, question: InterviewQuestion, answer_text: str) -> dict:
    return evaluate_interview_answer(
        job_title=session.job.title if session.job else session.target_job_title or "Interview",
        question_text=question.question_text,
        answer_text=answer_text,
        seniority=session.seniority or "mid",
    )


def get_next_unanswered_question(session: InterviewSession) -> InterviewQuestion | None:
    answered_question_ids = session.answers.values_list("question_id", flat=True)
    return session.questions.exclude(id__in=answered_question_ids).order_by("order").first()
