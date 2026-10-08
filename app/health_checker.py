import time
from datetime import datetime, timezone

import httpx


HEALTHY_STATUS_MIN = 200
HEALTHY_STATUS_MAX = 399


def check_service(url: str) -> dict:
    start_time = time.monotonic()

    try:
        with httpx.Client(
            timeout=5.0,
            follow_redirects=True
        ) as client:

            response = client.get(url)

        elapsed = time.monotonic() - start_time

        response_time_ms = round(
            elapsed * 1000,
            2
        )

        if (
            HEALTHY_STATUS_MIN
            <= response.status_code
            <= HEALTHY_STATUS_MAX
        ):
            status = "UP"
        else:
            status = "DOWN"

        return {
            "status": status,
            "http_status": response.status_code,
            "response_time_ms": response_time_ms,
            "checked_at": datetime.now(timezone.utc)
        }

    except httpx.RequestError:
        elapsed = time.monotonic() - start_time

        response_time_ms = round(
            elapsed * 1000,
            2
        )

        return {
            "status": "DOWN",
            "http_status": None,
            "response_time_ms": response_time_ms,
            "checked_at": datetime.now(timezone.utc)
        }
