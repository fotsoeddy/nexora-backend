from __future__ import annotations

import json
from urllib import error, request

from django.conf import settings

from ai_engine.services.provider_types import AIMessage, AIProviderError, AIProviderResponse


class OpenAICompatibleProvider:
    provider_name = "openai_compatible"

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_text(
        self,
        *,
        messages: list[AIMessage],
        model: str,
        temperature: float = 0.2,
        response_format: str = "text",
    ) -> AIProviderResponse:
        payload: dict = {
            "model": model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": temperature,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 20)) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise AIProviderError(f"Provider HTTP {exc.code}: {details[:200]}") from exc
        except error.URLError as exc:
            raise AIProviderError(f"Provider connection failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise AIProviderError("Provider returned invalid JSON.") from exc

        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = body.get("usage") or {}

        content = message.get("content")
        if not content:
            raise AIProviderError("Provider returned an empty response.")

        return AIProviderResponse(
            content=content,
            model_name=body.get("model") or model,
            provider_name=self.provider_name,
            tokens_input=int(usage.get("prompt_tokens") or 0),
            tokens_output=int(usage.get("completion_tokens") or 0),
            metadata={"raw_usage": usage},
        )
