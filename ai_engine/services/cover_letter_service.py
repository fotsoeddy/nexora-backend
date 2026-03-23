from __future__ import annotations

from django.conf import settings

from ai_engine.models import AICoverLetter
from ai_engine.services.provider_factory import get_ai_provider
from ai_engine.services.provider_types import AIMessage, AIProviderError
from ai_engine.services.usage import ai_usage_tracker


class CoverLetterService:
    @staticmethod
    def generate(*, user, candidate_profile, job_offer, job_title: str, company_name: str, tone: str) -> AICoverLetter:
        first_name = user.first_name or user.email.split("@")[0]
        messages = [
            AIMessage(
                role="system",
                content=(
                    "Write a concise, professional cover letter. Keep it credible, specific, "
                    "and free of exaggerated claims."
                ),
            ),
            AIMessage(
                role="user",
                content=(
                    f"Candidate name: {first_name}\n"
                    f"Job title: {job_title}\n"
                    f"Company: {company_name}\n"
                    f"Tone: {tone}\n"
                    "Write the final cover letter only."
                ),
            ),
        ]

        model_name = ""
        generated_text = ""
        try:
            with ai_usage_tracker(
                user=user,
                feature="cover_letter",
                request_metadata={"job_title": job_title, "company_name": company_name},
            ) as usage:
                provider = get_ai_provider()
                response = provider.generate_text(
                    messages=messages,
                    model=getattr(settings, "AI_WRITING_MODEL", getattr(settings, "AI_CHAT_MODEL", "gpt-4.1-mini")),
                    temperature=0.6,
                )
                generated_text = response.content
                model_name = response.model_name
                usage.update(
                    {
                        "model_name": response.model_name,
                        "tokens_input": response.tokens_input,
                        "tokens_output": response.tokens_output,
                        "cost_estimate": response.cost_estimate,
                        "request_metadata": {
                            "job_title": job_title,
                            "company_name": company_name,
                            "provider": response.provider_name,
                        },
                    }
                )
        except AIProviderError:
            if not getattr(settings, "AI_FALLBACK_TO_LOCAL", True):
                raise
            generated_text = (
                f"Dear Hiring Manager,\n\n"
                f"I am writing to express my interest in the {job_title} role at {company_name}. "
                f"My background, combined with a {tone} communication style, makes me confident in my ability to contribute quickly.\n\n"
                f"I bring relevant problem-solving skills, delivery discipline, and a strong motivation to support {company_name}'s goals.\n\n"
                f"Best regards,\n{first_name}"
            )
            model_name = "local-fallback"

        return AICoverLetter.objects.create(
            candidate=candidate_profile,
            job_offer=job_offer,
            tone=tone,
            generated_text=generated_text,
            user_instructions=company_name,
            model_version=model_name or job_title,
            status="completed",
        )
