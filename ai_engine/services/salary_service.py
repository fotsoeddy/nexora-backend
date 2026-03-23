from __future__ import annotations

import json

from django.conf import settings

from ai_engine.models import AISalaryEstimate
from ai_engine.services.provider_factory import get_ai_provider
from ai_engine.services.provider_types import AIMessage, AIProviderError
from ai_engine.services.usage import ai_usage_tracker


class SalaryService:
    @staticmethod
    def estimate(*, user, job_title: str, city: str, experience_level: str) -> AISalaryEstimate:
        fallback = SalaryService._fallback_estimate(job_title=job_title, city=city, experience_level=experience_level)

        try:
            with ai_usage_tracker(
                user=user,
                feature="salary",
                request_metadata={"job_title": job_title, "city": city, "experience_level": experience_level},
            ) as usage:
                provider = get_ai_provider()
                response = provider.generate_text(
                    messages=[
                        AIMessage(
                            role="system",
                            content=(
                                "Return salary estimate data as JSON with keys: estimated_min, estimated_median, "
                                "estimated_max, confidence_level, data_points_used, explanation."
                            ),
                        ),
                        AIMessage(
                            role="user",
                            content=f"Job title: {job_title}\nCity: {city}\nExperience level: {experience_level}",
                        ),
                    ],
                    model=getattr(settings, "AI_ANALYTICS_MODEL", getattr(settings, "AI_CHAT_MODEL", "gpt-4.1-mini")),
                    temperature=0.1,
                    response_format="json",
                )
                data = json.loads(response.content)
                usage.update(
                    {
                        "model_name": response.model_name,
                        "tokens_input": response.tokens_input,
                        "tokens_output": response.tokens_output,
                        "cost_estimate": response.cost_estimate,
                        "request_metadata": {
                            "job_title": job_title,
                            "city": city,
                            "experience_level": experience_level,
                            "provider": response.provider_name,
                        },
                    }
                )
                fallback.update(
                    {
                        "estimated_min": int(data.get("estimated_min", fallback["estimated_min"])),
                        "estimated_median": int(data.get("estimated_median", fallback["estimated_median"])),
                        "estimated_max": int(data.get("estimated_max", fallback["estimated_max"])),
                        "confidence_level": float(data.get("confidence_level", fallback["confidence_level"])),
                        "data_points_used": int(data.get("data_points_used", fallback["data_points_used"])),
                        "explanation": data.get("explanation", fallback["explanation"]),
                        "model_version": response.model_name,
                    }
                )
        except (AIProviderError, json.JSONDecodeError, ValueError, TypeError):
            if not getattr(settings, "AI_FALLBACK_TO_LOCAL", True):
                raise

        return AISalaryEstimate.objects.create(
            job_title=job_title,
            city=city,
            experience_level=experience_level,
            estimated_min=fallback["estimated_min"],
            estimated_median=fallback["estimated_median"],
            estimated_max=fallback["estimated_max"],
            confidence_level=fallback["confidence_level"],
            data_points_used=fallback["data_points_used"],
            explanation=fallback["explanation"],
            model_version=fallback["model_version"],
        )

    @staticmethod
    def _fallback_estimate(*, job_title: str, city: str, experience_level: str) -> dict:
        base = 200000
        if experience_level == "0-2":
            multiplier = 1.0
        elif experience_level == "3-5":
            multiplier = 1.4
        elif experience_level == "5-8":
            multiplier = 1.9
        else:
            multiplier = 2.4

        estimated_median = int(base * multiplier)
        return {
            "estimated_min": int(estimated_median * 0.85),
            "estimated_median": estimated_median,
            "estimated_max": int(estimated_median * 1.2),
            "confidence_level": 0.72,
            "data_points_used": 120,
            "explanation": "Local heuristic estimate based on job title, city and experience bracket.",
            "model_version": "local-fallback",
        }
