from __future__ import annotations

from typing import Protocol

from ai_engine.services.provider_types import AIMessage, AIProviderResponse


class AIProvider(Protocol):
    provider_name: str

    def generate_text(
        self,
        *,
        messages: list[AIMessage],
        model: str,
        temperature: float = 0.2,
        response_format: str = "text",
    ) -> AIProviderResponse:
        ...
