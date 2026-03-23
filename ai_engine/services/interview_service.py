from __future__ import annotations

import json

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from ai_engine.models import AIInterviewMessage, AIInterviewSession
from ai_engine.services.provider_factory import get_ai_provider
from ai_engine.services.provider_types import AIMessage, AIProviderError
from ai_engine.services.usage import ai_usage_tracker


class InterviewService:
    @staticmethod
    def generate_session(*, user, candidate_profile, job_offer, custom_job_title: str, difficulty: str, questions_count: int):
        session = AIInterviewSession.objects.create(
            candidate=candidate_profile,
            job_offer=job_offer,
            custom_job_title=custom_job_title,
            difficulty=difficulty,
            status="processing",
            started_at=timezone.now(),
            questions_count=questions_count,
        )

        job_title = job_offer.title if job_offer else custom_job_title
        questions = InterviewService._generate_questions(
            user=user,
            job_title=job_title,
            difficulty=difficulty,
            questions_count=questions_count,
        )
        AIInterviewMessage.objects.bulk_create(
            [
                AIInterviewMessage(
                    session=session,
                    role="ai",
                    content=question,
                    question_number=index + 1,
                )
                for index, question in enumerate(questions)
            ]
        )
        return session

    @staticmethod
    def submit_answer(*, user, session: AIInterviewSession, content: str) -> AIInterviewSession:
        questions = list(session.messages.filter(role="ai", question_number__isnull=False).order_by("question_number"))
        answers_count = session.messages.filter(role="user").count()

        if session.status == "completed":
            raise serializers.ValidationError({"detail": "This interview session is already completed."})
        if answers_count >= session.questions_count:
            raise serializers.ValidationError({"detail": "All questions have already been answered."})
        if answers_count >= len(questions):
            raise serializers.ValidationError({"detail": "No remaining interview question was found."})

        current_question = questions[answers_count]
        evaluation = InterviewService._evaluate_answer(
            user=user,
            session=session,
            question=current_question.content,
            answer=content,
        )

        AIInterviewMessage.objects.create(
            session=session,
            role="user",
            content=content,
            question_number=current_question.question_number,
            answer_score=evaluation["score"],
            answer_feedback=evaluation["feedback"],
        )

        next_answers_count = answers_count + 1
        if next_answers_count >= session.questions_count:
            InterviewService._finalize_session(user=user, session=session)
        else:
            session.status = "processing"
            session.save(update_fields=["status", "updated_at"])

        return session

    @staticmethod
    def _generate_questions(*, user, job_title: str, difficulty: str, questions_count: int) -> list[str]:
        fallback_questions = InterviewService._fallback_questions(job_title=job_title, difficulty=difficulty)[:questions_count]

        try:
            with ai_usage_tracker(
                user=user,
                feature="interview_generation",
                request_metadata={"job_title": job_title, "difficulty": difficulty, "questions_count": questions_count},
            ) as usage:
                provider = get_ai_provider()
                response = provider.generate_text(
                    messages=[
                        AIMessage(
                            role="system",
                            content=(
                                "Return JSON with a key named questions containing a list of concise interview questions. "
                                "Questions must be specific to the target role and difficulty."
                            ),
                        ),
                        AIMessage(
                            role="user",
                            content=(
                                f"Job title: {job_title}\n"
                                f"Difficulty: {difficulty}\n"
                                f"Questions count: {questions_count}"
                            ),
                        ),
                    ],
                    model=getattr(settings, "AI_CHAT_MODEL", "gpt-4.1-mini"),
                    temperature=0.4,
                    response_format="json",
                )
                data = json.loads(response.content)
                questions = [str(item).strip() for item in data.get("questions", []) if str(item).strip()]
                if len(questions) >= questions_count:
                    usage.update(
                        {
                            "model_name": response.model_name,
                            "tokens_input": response.tokens_input,
                            "tokens_output": response.tokens_output,
                            "cost_estimate": response.cost_estimate,
                            "request_metadata": {
                                "job_title": job_title,
                                "difficulty": difficulty,
                                "provider": response.provider_name,
                                "questions_count": questions_count,
                            },
                        }
                    )
                    return questions[:questions_count]
        except (AIProviderError, json.JSONDecodeError, ValueError, TypeError):
            if not getattr(settings, "AI_FALLBACK_TO_LOCAL", True):
                raise

        return fallback_questions

    @staticmethod
    def _evaluate_answer(*, user, session: AIInterviewSession, question: str, answer: str) -> dict:
        fallback = InterviewService._fallback_answer_evaluation(question=question, answer=answer)

        try:
            with ai_usage_tracker(
                user=user,
                feature="interview_evaluation",
                request_metadata={"session_id": str(session.uuid), "difficulty": session.difficulty},
            ) as usage:
                provider = get_ai_provider()
                response = provider.generate_text(
                    messages=[
                        AIMessage(
                            role="system",
                            content=(
                                "Return JSON with keys: score, feedback. Score must be an integer between 0 and 100. "
                                "Feedback must be concise and actionable."
                            ),
                        ),
                        AIMessage(
                            role="user",
                            content=(
                                f"Job title: {session.job_offer.title if session.job_offer_id else session.custom_job_title}\n"
                                f"Difficulty: {session.difficulty}\n"
                                f"Question: {question}\n"
                                f"Answer: {answer}"
                            ),
                        ),
                    ],
                    model=getattr(settings, "AI_ANALYTICS_MODEL", getattr(settings, "AI_CHAT_MODEL", "gpt-4.1-mini")),
                    temperature=0.1,
                    response_format="json",
                )
                data = json.loads(response.content)
                score = max(0, min(100, int(data.get("score", fallback["score"]))))
                feedback = str(data.get("feedback", fallback["feedback"])).strip() or fallback["feedback"]
                usage.update(
                    {
                        "model_name": response.model_name,
                        "tokens_input": response.tokens_input,
                        "tokens_output": response.tokens_output,
                        "cost_estimate": response.cost_estimate,
                        "request_metadata": {
                            "session_id": str(session.uuid),
                            "difficulty": session.difficulty,
                            "provider": response.provider_name,
                        },
                    }
                )
                return {"score": score, "feedback": feedback}
        except (AIProviderError, json.JSONDecodeError, ValueError, TypeError):
            if not getattr(settings, "AI_FALLBACK_TO_LOCAL", True):
                raise

        return fallback

    @staticmethod
    def _finalize_session(*, user, session: AIInterviewSession) -> None:
        answer_messages = list(session.messages.filter(role="user").order_by("created_at"))
        scores = [message.answer_score or 0 for message in answer_messages]
        overall_score = round(sum(scores) / max(len(scores), 1), 2)

        strengths = []
        improvements = []
        for index, message in enumerate(answer_messages, start=1):
            feedback = message.answer_feedback or ""
            if (message.answer_score or 0) >= 75 and len(strengths) < 3:
                strengths.append(f"Q{index}: {feedback}")
            elif len(improvements) < 3:
                improvements.append(f"Q{index}: {feedback}")

        session.status = "completed"
        session.completed_at = timezone.now()
        session.overall_score = overall_score
        session.communication_score = overall_score
        session.technical_score = max(0, min(100, overall_score - 4))
        session.confidence_score = max(0, min(100, overall_score + 3))
        session.strengths_noted = strengths or ["Clear baseline communication throughout the session."]
        session.areas_to_improve = improvements or ["Add more quantifiable impact and more specific examples."]
        session.ai_feedback = (
            "Interview completed. Focus on sharper examples, measurable impact, and clearer structure in each answer."
            if overall_score < 80
            else "Interview completed. Strong baseline performance with room to add more quantified business impact."
        )
        session.save(
            update_fields=[
                "status",
                "completed_at",
                "overall_score",
                "communication_score",
                "technical_score",
                "confidence_score",
                "strengths_noted",
                "areas_to_improve",
                "ai_feedback",
                "updated_at",
            ]
        )

        AIInterviewMessage.objects.create(
            session=session,
            role="ai",
            content=session.ai_feedback,
        )

    @staticmethod
    def _fallback_questions(*, job_title: str, difficulty: str) -> list[str]:
        intro = f"Can you introduce yourself for the {job_title} role?"
        role_fit = f"What makes you a strong fit for the {job_title} position?"
        challenge = f"Describe a challenging project related to {job_title}."
        base = [
            intro,
            role_fit,
            challenge,
            "How do you prioritize your work when deadlines are tight?",
            "What would you improve in your last team process?",
            "How do you handle constructive feedback during a project?",
            "Tell me about a failure and what you learned from it.",
            "How do you stay current in your field?",
            "What value would you bring in your first 90 days?",
            "Do you have any questions for the recruiter?",
        ]
        if difficulty == "hard":
            base[2] = f"Describe the most complex decision you made in a {job_title} project and defend it."
        elif difficulty == "easy":
            base[2] = f"What hands-on experience have you had that prepares you for a {job_title} role?"
        return base

    @staticmethod
    def _fallback_answer_evaluation(*, question: str, answer: str) -> dict:
        word_count = len(answer.split())
        has_numbers = any(character.isdigit() for character in answer)
        score = 55
        if word_count >= 20:
            score += 15
        if word_count >= 40:
            score += 10
        if has_numbers:
            score += 10
        if any(keyword in answer.lower() for keyword in ["result", "impact", "improved", "led", "built", "designed"]):
            score += 10
        score = max(35, min(92, score))

        feedback_parts = []
        if word_count < 20:
            feedback_parts.append("Expand the answer with a clearer situation, action and result.")
        else:
            feedback_parts.append("The answer has enough structure to be understood.")
        if not has_numbers:
            feedback_parts.append("Add measurable impact or concrete outcomes.")
        else:
            feedback_parts.append("The quantified detail strengthens credibility.")
        if "team" not in answer.lower():
            feedback_parts.append("Mention collaboration or stakeholder alignment where relevant.")

        return {
            "score": score,
            "feedback": " ".join(feedback_parts),
        }
