from unittest.mock import patch

import httpx

from app.health_checker import check_service


def test_health_check_success():
    mock_response = httpx.Response(
        status_code=200,
        request=httpx.Request(
            "GET",
            "https://test-service.local"
        )
    )

    with patch(
        "app.health_checker.httpx.Client"
    ) as mock_client:

        mock_client.return_value.__enter__.return_value.get.return_value = (
            mock_response
        )

        result = check_service(
            "https://test-service.local"
        )

    assert result["status"] == "UP"
    assert result["http_status"] == 200
    assert result["response_time_ms"] >= 0
    assert result["checked_at"] is not None


def test_health_check_server_error():
    mock_response = httpx.Response(
        status_code=500,
        request=httpx.Request(
            "GET",
            "https://test-service.local"
        )
    )

    with patch(
        "app.health_checker.httpx.Client"
    ) as mock_client:

        mock_client.return_value.__enter__.return_value.get.return_value = (
            mock_response
        )

        result = check_service(
            "https://test-service.local"
        )

    assert result["status"] == "DOWN"
    assert result["http_status"] == 500
    assert result["response_time_ms"] >= 0
    assert result["checked_at"] is not None


def test_health_check_connection_failure():
    with patch(
        "app.health_checker.httpx.Client"
    ) as mock_client:

        mock_client.return_value.__enter__.return_value.get.side_effect = (
            httpx.ConnectError(
                "Connection failed"
            )
        )

        result = check_service(
            "https://test-service.local"
        )

    assert result["status"] == "DOWN"
    assert result["http_status"] is None
    assert result["response_time_ms"] >= 0
    assert result["checked_at"] is not None
