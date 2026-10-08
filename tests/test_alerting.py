from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app import crud, models


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def setup_database():
    Base.metadata.create_all(bind=engine)


def teardown_database():
    Base.metadata.drop_all(bind=engine)


def test_three_consecutive_failures():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Alert Test Service",
        url="https://example.com",
        description="Testing failure detection"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    checked_at = datetime.now(timezone.utc)

    checks = [
        models.HealthCheck(
            service_id=service.id,
            status="UP",
            http_status=200,
            response_time_ms=100.0,
            checked_at=checked_at
        ),
        models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=100.0,
            checked_at=checked_at
        ),
        models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=100.0,
            checked_at=checked_at
        ),
        models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=100.0,
            checked_at=checked_at
        )
    ]

    db.add_all(checks)
    db.commit()

    failures = crud.get_consecutive_failures(
        db,
        service.id
    )

    assert failures == 3

    db.close()
    teardown_database()


def test_failure_sequence_stops_at_up():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Recovery Test Service",
        url="https://example.com",
        description="Testing recovery"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    checked_at = datetime.now(timezone.utc)

    checks = [
    models.HealthCheck(
        service_id=service.id,
        status="UP",
        http_status=200,
        response_time_ms=100.0,
        checked_at=checked_at
    ),
    models.HealthCheck(
        service_id=service.id,
        status="DOWN",
        http_status=500,
        response_time_ms=100.0,
        checked_at=checked_at
    ),
    models.HealthCheck(
        service_id=service.id,
        status="DOWN",
        http_status=500,
        response_time_ms=100.0,
        checked_at=checked_at
    )
 ]

    db.add_all(checks)
    db.commit()

    failures = crud.get_consecutive_failures(
        db,
        service.id
    )

    assert failures == 2

    db.close()
    teardown_database()


def test_alert_created_after_three_consecutive_failures():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Alert Lifecycle Service",
        url="https://example.com",
        description="Testing alert lifecycle"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    checked_at = datetime.now(timezone.utc)

    for _ in range(3):
        check = models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=100.0,
            checked_at=checked_at
        )

        db.add(check)
        db.commit()

        consecutive_failures = crud.get_consecutive_failures(
            db,
            service.id
        )

        active_alert = crud.get_active_alert(
            db,
            service.id,
            "SERVICE_DOWN"
        )

        if (
            consecutive_failures >= 3
            and not active_alert
        ):
            crud.create_alert(
                db,
                service.id,
                "SERVICE_DOWN",
                (
                    f"Service '{service.name}' has failed "
                    f"{consecutive_failures} consecutive health checks."
                )
            )

    alerts = (
        db.query(models.Alert)
        .filter(
            models.Alert.service_id == service.id
        )
        .all()
    )

    assert len(alerts) == 1
    assert alerts[0].status == "ACTIVE"
    assert alerts[0].alert_type == "SERVICE_DOWN"

    db.close()
    teardown_database()


def test_no_duplicate_active_alert():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Duplicate Alert Service",
        url="https://example.com",
        description="Testing duplicate alerts"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    checked_at = datetime.now(timezone.utc)

    for _ in range(4):
        check = models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=100.0,
            checked_at=checked_at
        )

        db.add(check)
        db.commit()

        consecutive_failures = crud.get_consecutive_failures(
            db,
            service.id
        )

        active_alert = crud.get_active_alert(
            db,
            service.id,
            "SERVICE_DOWN"
        )

        if (
            consecutive_failures >= 3
            and not active_alert
        ):
            crud.create_alert(
                db,
                service.id,
                "SERVICE_DOWN",
                "Service is down."
            )

    alerts = (
        db.query(models.Alert)
        .filter(
            models.Alert.service_id == service.id,
            models.Alert.status == "ACTIVE"
        )
        .all()
    )

    assert len(alerts) == 1

    db.close()
    teardown_database()


def test_alert_resolves_after_recovery():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Recovery Alert Service",
        url="https://example.com",
        description="Testing alert recovery"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    alert = crud.create_alert(
        db,
        service.id,
        "SERVICE_DOWN",
        "Service has failed three consecutive checks."
    )

    assert alert.status == "ACTIVE"
    assert alert.resolved_at is None

    resolved_alert = crud.resolve_alert(
        db,
        alert
    )

    assert resolved_alert.status == "RESOLVED"
    assert resolved_alert.resolved_at is not None

    db.close()
    teardown_database()
