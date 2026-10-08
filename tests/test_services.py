import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from datetime import datetime, timezone
from unittest.mock import patch

TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture()
def test_client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=test_engine)


def test_create_service(test_client):
    response = test_client.post(
        "/api/services",
        json={
            "name": "Test API",
            "url": "https://example.com",
            "description": "Test service"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test API"
    assert data["url"] == "https://example.com/"
    assert data["description"] == "Test service"


def test_list_services(test_client):
    test_client.post(
        "/api/services",
        json={
            "name": "Service One",
            "url": "https://example.com"
        }
    )

    response = test_client.get("/api/services")

    assert response.status_code == 200

    services = response.json()

    assert len(services) == 1
    assert services[0]["name"] == "Service One"


def test_get_service(test_client):
    create_response = test_client.post(
        "/api/services",
        json={
            "name": "Test API",
            "url": "https://example.com"
        }
    )

    service_id = create_response.json()["id"]

    response = test_client.get(
        f"/api/services/{service_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == service_id
    assert data["name"] == "Test API"


def test_update_service(test_client):
    create_response = test_client.post(
        "/api/services",
        json={
            "name": "Old Name",
            "url": "https://example.com",
            "description": "Old description"
        }
    )

    service_id = create_response.json()["id"]

    response = test_client.put(
        f"/api/services/{service_id}",
        json={
            "name": "Updated Name",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


def test_delete_service(test_client):
    create_response = test_client.post(
        "/api/services",
        json={
            "name": "Delete Me",
            "url": "https://example.com"
        }
    )

    service_id = create_response.json()["id"]

    response = test_client.delete(
        f"/api/services/{service_id}"
    )

    assert response.status_code == 204

    response = test_client.get(
        f"/api/services/{service_id}"
    )

    assert response.status_code == 404


def test_missing_service(test_client):
    response = test_client.get(
        "/api/services/999999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Service not found"
    }


def test_invalid_service(test_client):
    response = test_client.post(
        "/api/services",
        json={
            "name": "",
            "url": "invalid-url"
        }
    )

    assert response.status_code == 422


def test_duplicate_service(test_client):
    service = {
        "name": "Duplicate API",
        "url": "https://example.com"
    }

    first_response = test_client.post(
        "/api/services",
        json=service
    )

    assert first_response.status_code == 201

    second_response = test_client.post(
        "/api/services",
        json=service
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "A service with this name already exists"
    }
from unittest.mock import patch
from datetime import datetime, timezone


def test_service_health_check_api(test_client):
    create_response = test_client.post(
        "/api/services",
        json={
            "name": "Health Test Service",
            "url": "https://test-service.local"
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    mock_result = {
        "status": "UP",
        "http_status": 200,
        "response_time_ms": 42.5,
        "checked_at": datetime.now(timezone.utc)
    }

    with patch(
        "app.routers.services.check_service",
        return_value=mock_result
    ):
        response = test_client.post(
            f"/api/services/{service_id}/check"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["last_status"] == "UP"
    assert data["last_http_status"] == 200
    assert data["last_response_time_ms"] == 42.5
    assert data["last_checked_at"] is not None
def test_service_health_check_api_down(test_client):
    create_response = test_client.post(
        "/api/services",
        json={
            "name": "Down Test Service",
            "url": "https://test-service.local"
        }
    )

    assert create_response.status_code == 201

    service_id = create_response.json()["id"]

    mock_result = {
        "status": "DOWN",
        "http_status": 500,
        "response_time_ms": 250.75,
        "checked_at": datetime.now(timezone.utc)
    }

    with patch(
        "app.routers.services.check_service",
        return_value=mock_result
    ):
        response = test_client.post(
            f"/api/services/{service_id}/check"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["last_status"] == "DOWN"
    assert data["last_http_status"] == 500
    assert data["last_response_time_ms"] == 250.75
    assert data["last_checked_at"] is not None
def test_health_check_history_api(test_client):
    response = test_client.post(
        "/api/services",
        json={
            "name": "History API Service",
            "url": "https://example.com",
            "description": "Testing health check history"
        }
    )

    assert response.status_code == 201

    service = response.json()
    service_id = service["id"]

    with patch(
        "app.routers.services.check_service"
    ) as mock_check:

        mock_check.return_value = {
            "status": "UP",
            "http_status": 200,
            "response_time_ms": 120.0,
            "checked_at": datetime.now(timezone.utc)
        }

        response = test_client.post(
            f"/api/services/{service_id}/check"
        )

        assert response.status_code == 200

    response = test_client.get(
        f"/api/services/{service_id}/history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["service_id"] == service_id
    assert history[0]["status"] == "UP"
    assert history[0]["http_status"] == 200
    assert history[0]["response_time_ms"] == 120.0


def test_metrics_api(test_client):
    response = test_client.post(
        "/api/services",
        json={
            "name": "Metrics API Service",
            "url": "https://example.com",
            "description": "Testing metrics API"
        }
    )

    assert response.status_code == 201

    service = response.json()
    service_id = service["id"]

    with patch(
        "app.routers.services.check_service"
    ) as mock_check:

        mock_check.side_effect = [
            {
                "status": "UP",
                "http_status": 200,
                "response_time_ms": 100.0,
                "checked_at": datetime.now(timezone.utc)
            },
            {
                "status": "UP",
                "http_status": 200,
                "response_time_ms": 200.0,
                "checked_at": datetime.now(timezone.utc)
            },
            {
                "status": "DOWN",
                "http_status": 500,
                "response_time_ms": 300.0,
                "checked_at": datetime.now(timezone.utc)
            }
        ]

        for _ in range(3):
            response = test_client.post(
                f"/api/services/{service_id}/check"
            )

            assert response.status_code == 200

    response = test_client.get(
        f"/api/services/{service_id}/metrics"
    )

    assert response.status_code == 200

    metrics = response.json()

    assert metrics["service_id"] == service_id
    assert metrics["total_checks"] == 3
    assert metrics["successful_checks"] == 2
    assert metrics["failed_checks"] == 1
    assert metrics["uptime_percentage"] == 66.67
    assert metrics["average_response_time_ms"] == 200.0

