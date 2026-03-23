from __future__ import annotations

from django.conf import settings

from ai_engine.models import AIChatMessage, AIChatSession
from ai_engine.services.provider_factory import get_ai_provider
from ai_engine.services.provider_types import AIMessage, AIProviderError
from ai_engine.services.usage import ai_usage_tracker


class ChatService:
    @staticmethod
    def bootstrap_session(*, user, title: str, context_type: str) -> AIChatSession:
        session = AIChatSession.objects.create(
            user=user,
            title=title or "Career assistant",
            context_type=context_type or "career_advice",
        )
        intro = (
            "Hi! I'm Nexora, your AI career assistant. I can help with jobs, CVs, "
            "salary guidance, and interview preparation."
        )
        AIChatMessage.objects.create(
            session=session,
            role="ai",
            content=intro,
            metadata={"suggestions": ["Analyze my CV", "Recommend jobs", "Salary advice"]},
        )
        session.messages_count = 1
        session.save(update_fields=["messages_count", "updated_at"])
        return session

    @staticmethod
    def respond_to_message(*, session: AIChatSession, user, content: str) -> AIChatMessage:
        AIChatMessage.objects.create(session=session, role="user", content=content)
        history = [
            AIMessage(
                role="system",
                content=(
                    "You are Nexora, a concise AI career assistant. Give practical, specific advice. "
                    "When useful, provide three next-step suggestions."
                ),
            )
        ]
        history.extend(
            AIMessage(role=message.role if message.role != "ai" else "assistant", content=message.content)
            for message in session.messages.order_by("created_at")
        )

        try:
            with ai_usage_tracker(
                user=user,
                feature="chat",
                request_metadata={"context_type": session.context_type, "session_id": str(session.uuid)},
            ) as usage:
                provider = get_ai_provider()
                response = provider.generate_text(
                    messages=history,
                    model=getattr(settings, "AI_CHAT_MODEL", "gpt-4.1-mini"),
                    temperature=0.4,
                )
                usage.update(
                    {
                        "model_name": response.model_name,
                        "tokens_input": response.tokens_input,
                        "tokens_output": response.tokens_output,
                        "cost_estimate": response.cost_estimate,
                        "request_metadata": {
                            "context_type": session.context_type,
                            "provider": response.provider_name,
                            "session_id": str(session.uuid),
                        },
                    }
                )
        except AIProviderError:
            if not getattr(settings, "AI_FALLBACK_TO_LOCAL", True):
                raise
            from ai_engine.services.providers.local import LocalAIProvider

            response = LocalAIProvider().generate_text(
                messages=history,
                model="local-fallback",
                temperature=0.4,
            )

        ai_message = AIChatMessage.objects.create(
            session=session,
            role="ai",
            content=response.content,
            metadata={"suggestions": response.metadata.get("suggestions", [])},
            tokens_used=response.tokens_output or None,
        )
        session.messages_count = session.messages.count()
        session.save(update_fields=["messages_count", "updated_at"])
        return ai_message
