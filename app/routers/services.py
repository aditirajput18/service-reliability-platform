from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .. import crud, schemas, models
from ..database import get_db
from ..health_checker import check_service


router = APIRouter(
    prefix="/api/services",
    tags=["Services"]
)


@router.post(
    "",
    response_model=schemas.ServiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    existing_service = crud.get_service_by_name(
        db,
        service.name
    )

    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A service with this name already exists"
        )

    return crud.create_service(db, service)


@router.get(
    "",
    response_model=list[schemas.ServiceResponse]
)
def list_services(
    db: Session = Depends(get_db)
):
    return crud.get_services(db)


@router.get(
    "/{service_id}",
    response_model=schemas.ServiceResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return service


@router.put(
    "/{service_id}",
    response_model=schemas.ServiceResponse
)
def update_service(
    service_id: int,
    service: schemas.ServiceUpdate,
    db: Session = Depends(get_db)
):
    db_service = crud.get_service(
        db,
        service_id
    )

    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    if service.name:
        existing_service = crud.get_service_by_name(
            db,
            service.name
        )

        if (
            existing_service
            and existing_service.id != service_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A service with this name already exists"
            )

    return crud.update_service(
        db,
        db_service,
        service
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    crud.delete_service(
        db,
        service
    )


@router.get(
    "/{service_id}/metrics",
    response_model=schemas.ServiceMetricsResponse
)
def get_service_metrics(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return crud.get_service_metrics(
        db,
        service_id
    )
@router.get(
    "/{service_id}/history",
    response_model=list[schemas.HealthCheckResponse]
)
def get_service_history(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return crud.get_health_check_history(
        db,
        service_id
    )
@router.post(
    "/{service_id}/check",
    response_model=schemas.ServiceResponse
)
def check_registered_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    health_result = check_service(
        service.url
    )

    # Update latest health status
    updated_service = crud.update_health_check(
        db,
        service,
        health_result
    )

    # Store health check history
    crud.create_health_check(
        db,
        service_id,
        health_result
    )

    # Check for consecutive failures
    consecutive_failures = crud.get_consecutive_failures(
        db,
        service_id
    )

    alert_type = "SERVICE_DOWN"

    active_alert = crud.get_active_alert(
        db,
        service_id,
        alert_type
    )

    # Create an alert after 3 consecutive failures
    # Check for consecutive failures
    consecutive_failures = crud.get_consecutive_failures(
        db,
        service_id
    )

    alert_type = "SERVICE_DOWN"

    active_alert = crud.get_active_alert(
        db,
        service_id,
        alert_type
    )

    # Create an alert and incident after 3 consecutive failures
    if consecutive_failures >= 3 and not active_alert:
        active_alert = crud.create_alert(
            db,
            service_id,
            alert_type,
            (
                f"Service '{service.name}' has failed "
                f"{consecutive_failures} consecutive health checks."
            )
        )

        open_incident = crud.get_open_incident(
            db,
            service_id,
            active_alert.id
        )

        if not open_incident:
            crud.create_incident(
                db,
                service_id,
                active_alert,
                service.name
            )

    # Resolve the alert and incident after recovery
    if health_result["status"] == "UP" and active_alert:
        crud.resolve_alert(
            db,
            active_alert
        )

        open_incident = crud.get_open_incident(
            db,
            service_id,
            active_alert.id
        )

        if open_incident:
            crud.resolve_incident(
                db,
                open_incident
            )

    return updated_service
    # Resolve an active alert after recovery
    if health_result["status"] == "UP" and active_alert:
        crud.resolve_alert(
            db,
            active_alert
        )

    return updated_service
@router.get(
    "/{service_id}/incidents",
    response_model=list[schemas.IncidentResponse]
)
def get_service_incidents(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return crud.get_service_incidents(
        db,
        service_id
    )


@router.patch(
    "/{service_id}/incidents/{incident_id}",
    response_model=schemas.IncidentResponse
)
def update_incident_status(
    service_id: int,
    incident_id: int,
    incident_update: schemas.IncidentStatusUpdate,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id == incident_id,
            models.Incident.service_id == service_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    allowed_statuses = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    }

    if incident_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid incident status"
        )

    if (
        incident.status == "RESOLVED"
        and incident_update.status != "RESOLVED"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved incidents cannot be reopened"
        )

    return crud.update_incident_status(
        db,
        incident,
        incident_update.status
    )
@router.get(
    "/{service_id}/alerts",
    response_model=list[schemas.AlertResponse]
)
def get_service_alerts(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = crud.get_service(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return (
        db.query(models.Alert)
        .filter(
            models.Alert.service_id == service_id
        )
        .order_by(
            models.Alert.created_at.desc()
        )
        .all()
    )
