from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AIMessage:
    role: str
    content: str


@dataclass(slots=True)
class AIProviderResponse:
    content: str
    model_name: str
    provider_name: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_estimate: float = 0
    metadata: dict = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised when the configured provider cannot complete a request."""
