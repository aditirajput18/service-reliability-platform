from prometheus_client import Counter, Gauge, Histogram

HEALTH_CHECKS_TOTAL = Counter(
    "srp_health_checks_total",
    "Total number of service health checks performed.",
    ["service_id", "status"],
)

SERVICE_STATUS = Gauge(
    "srp_service_status",
    "Current health status of a monitored service (1=UP, 0=DOWN).",
    ["service_id", "service_name"],
)

HEALTH_CHECK_DURATION_SECONDS = Histogram(
    "srp_health_check_duration_seconds",
    "Duration of service health checks in seconds.",
    ["service_id"],
)


def record_health_check(
    service_id: int,
    service_name: str,
    status: str,
    response_time_ms: float | None,
) -> None:
    """Record the result of a service health check."""

    service_id_label = str(service_id)

    HEALTH_CHECKS_TOTAL.labels(
        service_id=service_id_label,
        status=status,
    ).inc()

    SERVICE_STATUS.labels(
        service_id=service_id_label,
        service_name=service_name,
    ).set(1 if status == "UP" else 0)

    if response_time_ms is not None:
        HEALTH_CHECK_DURATION_SECONDS.labels(
            service_id=service_id_label,
        ).observe(response_time_ms / 1000)
