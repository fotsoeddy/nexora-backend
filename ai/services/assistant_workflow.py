from __future__ import annotations

from ai.models import (
    AssistantChatMessage,
    AssistantChatSession,
    AssistantMessageRole,
    CoverLetterDraft,
    Job,
    SalaryEstimate,
)
from ai.openai_utils import (
    estimate_salary_range,
    generate_chat_response,
    generate_cover_letter_text,
)


def bootstrap_chat_session(*, user, title: str, context_type: str) -> AssistantChatSession:
    session = AssistantChatSession.objects.create(
        user=user,
        title=title or "Career assistant",
        context_type=context_type or "career_advice",
    )
    welcome_payload = generate_chat_response(
        "Start the session with a short welcome message.",
        context_type=session.context_type,
        conversation=[],
    )
    AssistantChatMessage.objects.create(
        session=session,
        role=AssistantMessageRole.AI,
        content=welcome_payload["content"],
        metadata={"suggestions": welcome_payload.get("suggestions", [])},
    )
    return session


def respond_to_chat_message(*, session: AssistantChatSession, content: str) -> AssistantChatMessage:
    AssistantChatMessage.objects.create(
        session=session,
        role=AssistantMessageRole.USER,
        content=content,
    )
    conversation = list(
        session.messages.values("role", "content").order_by("created_at")
    )
    response_payload = generate_chat_response(
        content,
        context_type=session.context_type,
        conversation=conversation,
    )
    ai_message = AssistantChatMessage.objects.create(
        session=session,
        role=AssistantMessageRole.AI,
        content=response_payload["content"],
        metadata={"suggestions": response_payload.get("suggestions", [])},
    )
    return ai_message


def create_cover_letter(
    *,
    user,
    job_offer_id=None,
    job_title: str | None = None,
    company_name: str | None = None,
    tone: str = "professional",
) -> CoverLetterDraft:
    job = None
    if job_offer_id:
        job = Job.objects.filter(pk=job_offer_id).first()

    resolved_job_title = job_title or (job.title if job else "Target role")
    resolved_company_name = company_name or (job.company_name if job else "Target company")

    generated_text = generate_cover_letter_text(
        resolved_job_title,
        resolved_company_name,
        tone=tone or "professional",
    )
    return CoverLetterDraft.objects.create(
        user=user,
        job=job,
        job_title=resolved_job_title,
        company_name=resolved_company_name,
        tone=tone or "professional",
        generated_text=generated_text,
    )


def create_salary_estimate(*, user, job_title: str, city: str, experience_level: str) -> SalaryEstimate:
    payload = estimate_salary_range(job_title, city, experience_level)
    return SalaryEstimate.objects.create(
        user=user,
        job_title=payload["job_title"],
        city=payload["city"],
        experience_level=payload["experience_level"],
        estimated_min=payload["estimated_min"],
        estimated_median=payload["estimated_median"],
        estimated_max=payload["estimated_max"],
        confidence_level=payload["confidence_level"],
        data_points_used=payload["data_points_used"],
        explanation=payload["explanation"],
    )
