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


def create_test_service(db):
    service = models.Service(
        name="Test Service",
        url="https://example.com",
        description="Test service"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


def create_test_alert(db, service_id):
    alert = models.Alert(
        service_id=service_id,
        alert_type="SERVICE_DOWN",
        status="ACTIVE",
        message="Test service is down",
        created_at=datetime.now(timezone.utc)
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def test_create_incident():
    setup_database()

    db = TestingSessionLocal()

    service = create_test_service(db)
    alert = create_test_alert(db, service.id)

    incident = crud.create_incident(
        db,
        service.id,
        alert,
        service.name
    )

    assert incident.id is not None
    assert incident.service_id == service.id
    assert incident.alert_id == alert.id
    assert incident.status == "OPEN"
    assert incident.resolved_at is None

    db.close()
    teardown_database()


def test_get_open_incident():
    setup_database()

    db = TestingSessionLocal()

    service = create_test_service(db)
    alert = create_test_alert(db, service.id)

    incident = crud.create_incident(
        db,
        service.id,
        alert,
        service.name
    )

    found_incident = crud.get_open_incident(
        db,
        service.id,
        alert.id
    )

    assert found_incident is not None
    assert found_incident.id == incident.id

    db.close()
    teardown_database()


def test_resolve_incident():
    setup_database()

    db = TestingSessionLocal()

    service = create_test_service(db)
    alert = create_test_alert(db, service.id)

    incident = crud.create_incident(
        db,
        service.id,
        alert,
        service.name
    )

    resolved = crud.resolve_incident(
        db,
        incident
    )

    assert resolved.status == "RESOLVED"
    assert resolved.resolved_at is not None

    db.close()
    teardown_database()


def test_resolved_incident_not_returned_as_open():
    setup_database()

    db = TestingSessionLocal()

    service = create_test_service(db)
    alert = create_test_alert(db, service.id)

    incident = crud.create_incident(
        db,
        service.id,
        alert,
        service.name
    )

    crud.resolve_incident(
        db,
        incident
    )

    open_incident = crud.get_open_incident(
        db,
        service.id,
        alert.id
    )

    assert open_incident is None

    db.close()
    teardown_database()


def test_get_service_incidents():
    setup_database()

    db = TestingSessionLocal()

    service = create_test_service(db)
    alert = create_test_alert(db, service.id)

    crud.create_incident(
        db,
        service.id,
        alert,
        service.name
    )

    incidents = crud.get_service_incidents(
        db,
        service.id
    )

    assert len(incidents) == 1
    assert incidents[0].service_id == service.id

    db.close()
    teardown_database()
