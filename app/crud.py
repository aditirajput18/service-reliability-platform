from sqlalchemy.orm import Session
from datetime import datetime, timezone
from . import models
from .schemas import ServiceCreate, ServiceUpdate


def get_services(db: Session):
    return db.query(models.Service).all()


def get_service(db: Session, service_id: int):
    return (
        db.query(models.Service)
        .filter(models.Service.id == service_id)
        .first()
    )


def get_service_by_name(db: Session, name: str):
    return (
        db.query(models.Service)
        .filter(models.Service.name == name)
        .first()
    )


def create_service(
    db: Session,
    service: ServiceCreate
):
    db_service = models.Service(
        name=service.name,
        url=str(service.url),
        description=service.description
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


def update_service(
    db: Session,
    db_service: models.Service,
    service: ServiceUpdate
):
    update_data = service.model_dump(
        exclude_unset=True
    )

    if "url" in update_data:
        update_data["url"] = str(update_data["url"])

    for field, value in update_data.items():
        setattr(db_service, field, value)

    db.commit()
    db.refresh(db_service)

    return db_service


def delete_service(
    db: Session,
    db_service: models.Service
):
    db.delete(db_service)
    db.commit()
def update_health_check(
    db: Session,
    db_service: models.Service,
    health_result: dict
):
    db_service.last_status = health_result["status"]

    db_service.last_http_status = (
        health_result["http_status"]
    )

    db_service.last_response_time_ms = (
        health_result["response_time_ms"]
    )

    db_service.last_checked_at = (
        health_result["checked_at"]
    )

    db.commit()
    db.refresh(db_service)

    return db_service
def create_health_check(
    db: Session,
    service_id: int,
    health_result: dict
):
    db_health_check = models.HealthCheck(
        service_id=service_id,
        status=health_result["status"],
        http_status=health_result["http_status"],
        response_time_ms=health_result["response_time_ms"],
        checked_at=health_result["checked_at"],
    )

    db.add(db_health_check)
    db.commit()
    db.refresh(db_health_check)

    return db_health_check
def get_service_metrics(db: Session, service_id: int):
    checks = (
        db.query(models.HealthCheck)
        .filter(models.HealthCheck.service_id == service_id)
        .all()
    )

    total_checks = len(checks)

    successful_checks = sum(
        1 for check in checks
        if check.status == "UP"
    )

    failed_checks = sum(
        1 for check in checks
        if check.status == "DOWN"
    )

    if total_checks > 0:
        uptime_percentage = round(
            (successful_checks / total_checks) * 100,
            2
        )
    else:
        uptime_percentage = 0.0

    response_times = [
        check.response_time_ms
        for check in checks
        if check.response_time_ms is not None
    ]

    if response_times:
        average_response_time_ms = round(
            sum(response_times) / len(response_times),
            2
        )
    else:
        average_response_time_ms = 0.0

    return {
        "service_id": service_id,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percentage": uptime_percentage,
        "average_response_time_ms": average_response_time_ms
    }
def get_health_check_history(
    db: Session,
    service_id: int
):
    return (
        db.query(models.HealthCheck)
        .filter(
            models.HealthCheck.service_id == service_id
        )
        .order_by(
            models.HealthCheck.checked_at.desc()
        )
        .all()
    )
def get_active_alert(
    db: Session,
    service_id: int,
    alert_type: str
):
    return (
        db.query(models.Alert)
        .filter(
            models.Alert.service_id == service_id,
            models.Alert.alert_type == alert_type,
            models.Alert.status == "ACTIVE"
        )
        .first()
    )


def create_alert(
    db: Session,
    service_id: int,
    alert_type: str,
    message: str
):
    alert = models.Alert(
        service_id=service_id,
        alert_type=alert_type,
        status="ACTIVE",
        message=message,
        created_at=datetime.now(timezone.utc)
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def resolve_alert(
    db: Session,
    alert: models.Alert
):
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alert)

    return alert
FAILURE_THRESHOLD = 3


def get_consecutive_failures(
    db: Session,
    service_id: int
):
    checks = (
        db.query(models.HealthCheck)
        .filter(
            models.HealthCheck.service_id == service_id
        )
        .order_by(
            models.HealthCheck.checked_at.desc(),
            models.HealthCheck.id.desc()
        )
        .limit(FAILURE_THRESHOLD)
        .all()
    )

    consecutive_failures = 0

    for check in checks:
        if check.status == "DOWN":
            consecutive_failures += 1
        else:
            break

    return consecutive_failures
def get_open_incident(
    db: Session,
    service_id: int,
    alert_id: int
):
    return (
        db.query(models.Incident)
        .filter(
            models.Incident.service_id == service_id,
            models.Incident.alert_id == alert_id,
            models.Incident.status != "RESOLVED"
        )
        .first()
    )


def create_incident(
    db: Session,
    service_id: int,
    alert: models.Alert,
    service_name: str
):
    incident = models.Incident(
        service_id=service_id,
        alert_id=alert.id,
        title=f"Service '{service_name}' is down",
        description=(
            f"Service '{service_name}' triggered a "
            f"SERVICE_DOWN alert after consecutive "
            f"health check failures."
        ),
        status="OPEN",
        created_at=datetime.now(timezone.utc)
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def get_service_incidents(
    db: Session,
    service_id: int
):
    return (
        db.query(models.Incident)
        .filter(
            models.Incident.service_id == service_id
        )
        .order_by(
            models.Incident.created_at.desc()
        )
        .all()
    )


def resolve_incident(
    db: Session,
    incident: models.Incident
):
    incident.status = "RESOLVED"
    incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    return incident
def update_incident_status(
    db: Session,
    incident: models.Incident,
    new_status: str
):
    incident.status = new_status

    if new_status == "RESOLVED":
        incident.resolved_at = datetime.now(timezone.utc)
    else:
        incident.resolved_at = None

    db.commit()
    db.refresh(incident)

    return incident
