from __future__ import annotations

from django.conf import settings

from ai_engine.services.provider_types import AIProviderError
from ai_engine.services.providers.local import LocalAIProvider
from ai_engine.services.providers.openai_compatible import OpenAICompatibleProvider


def get_ai_provider():
    provider_name = getattr(settings, "AI_PROVIDER", "local")
    if provider_name == "local":
        return LocalAIProvider()
    if provider_name == "openai_compatible":
        api_key = getattr(settings, "AI_API_KEY", "")
        base_url = getattr(settings, "AI_API_BASE_URL", "")
        if not api_key or not base_url:
            raise AIProviderError("AI_API_KEY and AI_API_BASE_URL are required for openai_compatible provider.")
        return OpenAICompatibleProvider(api_key=api_key, base_url=base_url)
    raise AIProviderError(f"Unknown AI provider: {provider_name}")
