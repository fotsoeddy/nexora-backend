from __future__ import annotations

import time
from contextlib import contextmanager

from ai_engine.models import AIUsageLog


@contextmanager
def ai_usage_tracker(*, user, feature: str, request_metadata: dict | None = None):
    started = time.perf_counter()
    data = {
        "user": user,
        "feature": feature,
        "request_metadata": request_metadata or {},
        "status": "processing",
    }
    try:
        yield data
        data.setdefault("status", "completed")
    except Exception as exc:
        data["status"] = "failed"
        data["error_message"] = str(exc)
        raise
    finally:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        AIUsageLog.objects.create(
            user=user,
            feature=feature,
            status=data.get("status", "completed"),
            tokens_input=int(data.get("tokens_input") or 0),
            tokens_output=int(data.get("tokens_output") or 0),
            cost_estimate=float(data.get("cost_estimate") or 0),
            processing_time_ms=elapsed_ms,
            model_name=data.get("model_name", ""),
            error_message=data.get("error_message", ""),
            request_metadata=data.get("request_metadata", {}),
        )
