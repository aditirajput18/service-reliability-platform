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


def test_service_metrics():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="Metrics Test Service",
        url="https://example.com",
        description="Testing monitoring metrics"
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
            status="UP",
            http_status=200,
            response_time_ms=200.0,
            checked_at=checked_at
        ),
        models.HealthCheck(
            service_id=service.id,
            status="DOWN",
            http_status=500,
            response_time_ms=300.0,
            checked_at=checked_at
        ),
        models.HealthCheck(
            service_id=service.id,
            status="UP",
            http_status=200,
            response_time_ms=150.0,
            checked_at=checked_at
        )
    ]

    db.add_all(checks)
    db.commit()

    metrics = crud.get_service_metrics(
        db,
        service.id
    )

    assert metrics["service_id"] == service.id
    assert metrics["total_checks"] == 4
    assert metrics["successful_checks"] == 3
    assert metrics["failed_checks"] == 1
    assert metrics["uptime_percentage"] == 75.0
    assert metrics["average_response_time_ms"] == 187.5

    db.close()
    teardown_database()


def test_metrics_with_no_checks():
    setup_database()

    db = TestingSessionLocal()

    service = models.Service(
        name="No Checks Service",
        url="https://example.com",
        description="Service without health checks"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    metrics = crud.get_service_metrics(
        db,
        service.id
    )

    assert metrics["service_id"] == service.id
    assert metrics["total_checks"] == 0
    assert metrics["successful_checks"] == 0
    assert metrics["failed_checks"] == 0
    assert metrics["uptime_percentage"] == 0.0
    assert metrics["average_response_time_ms"] == 0.0

    db.close()
    teardown_database()
