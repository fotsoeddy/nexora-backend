# AI Integration Architecture

## Goal

Connect Nexora's AI features to a real external AI provider without changing the existing frontend contracts.

## Stable API contract

The mobile app should continue using the current routes:

- `POST /api/ai/chat/sessions/`
- `GET /api/ai/chat/sessions/`
- `GET /api/ai/chat/sessions/{id}/`
- `POST /api/ai/chat/sessions/{id}/messages/`
- `POST /api/ai/cover-letters/generate/`
- `POST /api/ai/salary-estimates/`
- `POST /ai/api/interviews/sessions/generate/`
- `POST /api/ai/interviews/sessions/{id}/answers/`

Future interview scoring and voice APIs should follow the same pattern:

- frontend contracts stay stable
- provider switching happens behind the service layer

## Implemented service architecture

The backend now uses:

- `ai_engine/services/provider_factory.py`
- `ai_engine/services/providers/local.py`
- `ai_engine/services/providers/openai_compatible.py`
- `ai_engine/services/chat_service.py`
- `ai_engine/services/cover_letter_service.py`
- `ai_engine/services/salary_service.py`
- `ai_engine/services/interview_service.py`
- `ai_engine/services/usage.py`

## Provider strategy

### 1. `local`

Purpose:

- deterministic local fallback
- development and test safety
- zero external dependency

### 2. `openai_compatible`

Purpose:

- connect to any OpenAI-style chat completion API
- use one backend integration point for OpenAI-compatible vendors

Expected environment variables:

- `AI_PROVIDER=openai_compatible`
- `AI_API_KEY=...`
- `AI_API_BASE_URL=https://api.openai.com/v1`
- `AI_CHAT_MODEL=...`
- `AI_WRITING_MODEL=...`
- `AI_ANALYTICS_MODEL=...`
- `AI_REQUEST_TIMEOUT_SECONDS=20`
- `AI_FALLBACK_TO_LOCAL=true`

## Why this architecture is the right one

- Views remain thin and testable.
- Provider code is isolated from business logic.
- Frontend contracts remain stable.
- You can switch provider without rewriting screens.
- Usage is logged in `AIUsageLog`.
- Local fallback prevents hard outages in development or temporary provider failures.

## Recommended next improvements

### Priority 1

- persist prompt templates in dedicated modules instead of inline strings
- add rate limiting and per-user AI quotas

### Priority 2

- store provider request IDs and richer token accounting
- add structured JSON validation for AI outputs
- add retry logic with exponential backoff on transient upstream failures

### Priority 3

- queue expensive AI tasks asynchronously with Celery or Django-Q
- stream chat responses if the chosen provider supports it
- add moderation / prompt-injection guards for user content

## Suggested production setup

### Backend

- keep provider secrets only in environment variables
- enable request timeout and fallback
- log errors without exposing secrets
- monitor `AIUsageLog` for cost, latency and failure rates

### Frontend

- keep calling the same routes
- surface provider failure as friendly retryable messages
- avoid embedding API keys in the mobile app

## Important constraint

The current real remote APIs already developed by your collaborator are still intentionally untouched.
This architecture was added on the local codebase so the future pull can be merged with minimal rework.
