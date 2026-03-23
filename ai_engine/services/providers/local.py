from __future__ import annotations

import json

from ai_engine.services.provider_types import AIMessage, AIProviderResponse


class LocalAIProvider:
    provider_name = "local"

    def generate_text(
        self,
        *,
        messages: list[AIMessage],
        model: str,
        temperature: float = 0.2,
        response_format: str = "text",
    ) -> AIProviderResponse:
        prompt = "\n".join(message.content for message in messages if message.role == "user").strip()
        lowered = prompt.lower()

        if response_format == "json":
            payload = self._build_json_payload(lowered, prompt)
            return AIProviderResponse(
                content=json.dumps(payload),
                model_name=model or "local-heuristic",
                provider_name=self.provider_name,
                metadata={"response_format": "json"},
            )

        if "cover letter" in lowered or "job title:" in lowered:
            job_title = self._extract_field(prompt, "Job title") or "the role"
            company_name = self._extract_field(prompt, "Company") or "the company"
            candidate_name = self._extract_field(prompt, "Candidate name") or "Candidate"
            tone = self._extract_field(prompt, "Tone") or "professional"
            return AIProviderResponse(
                content=(
                    "Dear Hiring Manager,\n\n"
                    f"I am writing to express my interest in the {job_title} role at {company_name}. "
                    f"My background and {tone} communication style would allow me to contribute quickly and reliably.\n\n"
                    f"I would welcome the opportunity to support {company_name}'s objectives and discuss how I can add value.\n\n"
                    f"Best regards,\n{candidate_name}"
                ),
                model_name=model or "local-heuristic",
                provider_name=self.provider_name,
            )

        if "cv" in lowered or "resume" in lowered:
            content = (
                "Your CV can be improved by tightening the summary, adding measurable impact, "
                "and aligning the key skills with the target role."
            )
            suggestions = ["Improve my CV", "Cover letter help", "ATS analysis"]
        elif "salary" in lowered:
            content = (
                "Salary discussions should be anchored on market range, experience level, "
                "and expected business impact."
            )
            suggestions = ["Estimate my salary", "Negotiation tips", "Compare locations"]
        elif "job" in lowered or "recommend" in lowered:
            content = (
                "Focus on roles that match your strongest skills first, then broaden by adjacent "
                "domains and cities."
            )
            suggestions = ["Show jobs", "Set alerts", "Interview prep"]
        else:
            content = "Tell me more about your career goal and I will suggest the next most useful action."
            suggestions = ["Find jobs", "Improve CV", "Interview practice"]

        return AIProviderResponse(
            content=content,
            model_name=model or "local-heuristic",
            provider_name=self.provider_name,
            metadata={"suggestions": suggestions},
        )

    def _build_json_payload(self, lowered: str, prompt: str) -> dict:
        if "questions count" in lowered:
            job_title = self._extract_field(prompt, "Job title") or "the role"
            questions_count = int(self._extract_field(prompt, "Questions count") or "5")
            questions = [
                f"Can you introduce yourself for the {job_title} role?",
                f"What makes you a strong fit for the {job_title} position?",
                f"Describe a challenging project related to {job_title}.",
                "How do you prioritize your work when deadlines are tight?",
                "What value would you bring in your first 90 days?",
                "How do you handle feedback during a project?",
            ]
            return {"questions": questions[:questions_count]}

        if "score, feedback" in lowered:
            return {
                "score": 78,
                "feedback": "The answer is clear. Add more measurable outcomes and a sharper description of your direct impact.",
            }

        if "salary" in lowered:
            return {
                "estimated_min": 320000,
                "estimated_median": 380000,
                "estimated_max": 460000,
                "confidence_level": 0.72,
                "data_points_used": 120,
                "explanation": "Local fallback estimate based on job title, city and experience bracket.",
            }

        return {
            "generated_text": (
                "Dear Hiring Manager,\n\n"
                "I am excited to submit my application. My background and execution discipline "
                "allow me to contribute quickly while collaborating effectively with your team.\n\n"
                "Best regards,"
            ),
            "suggestions": ["Review my CV", "Prepare interview", "Find jobs"],
        }

    def _extract_field(self, prompt: str, field_name: str) -> str:
        prefix = f"{field_name}:"
        for line in prompt.splitlines():
            if line.startswith(prefix):
                return line.replace(prefix, "", 1).strip()
        return ""
