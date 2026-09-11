"""API tests for routes endpoint."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.infrastructure.osrm import (
    OSRMInvalidCoordinatesError,
    OSRMNotFoundError,
    OSRMServerError,
    OSRMTimeoutError,
    RouteResponse,
)
from app.models import RouteGeometry


def test_create_route_success(client: TestClient) -> None:
    """Test successful route creation."""
    # Mock OSRM response
    mock_geometry = RouteGeometry(
        type="LineString",
        coordinates=[
            [-96.7970, 32.7767],
            [-95.3698, 29.7604],
        ],
    )

    mock_osrm_response = MagicMock(spec=RouteResponse)
    mock_osrm_response.distance_meters = 385742.4
    mock_osrm_response.duration_seconds = 13982.1
    mock_osrm_response.geometry = mock_geometry

    with patch(
        "app.api.routes.routes.RouteService.calculate_and_save_route",
        return_value=MagicMock(
            start_lat=32.7767,
            start_lon=-96.7970,
            end_lat=29.7604,
            end_lon=-95.3698,
            distance_meters=385742.4,
            duration_seconds=13982.1,
            geometry=mock_geometry,
            id="550e8400-e29b-41d4-a716-446655440000",
            created_at="2026-09-10T00:00:00",
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/routes/",
            json={
                "start_lat": 32.7767,
                "start_lon": -96.7970,
                "end_lat": 29.7604,
                "end_lon": -95.3698,
            },
        )

    assert response.status_code == 201
    content = response.json()
    assert content["start_lat"] == 32.7767
    assert content["start_lon"] == -96.7970
    assert content["end_lat"] == 29.7604
    assert content["end_lon"] == -95.3698
    assert content["distance_meters"] == 385742.4
    assert content["duration_seconds"] == 13982.1
    assert "geometry" in content


def test_create_route_invalid_coordinates(client: TestClient) -> None:
    """Test route creation with invalid coordinates."""
    with patch(
        "app.api.routes.routes.RouteService.calculate_and_save_route",
        side_effect=OSRMInvalidCoordinatesError("Invalid start latitude: 100"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/routes/",
            json={
                "start_lat": 100.0,  # Invalid
                "start_lon": -96.0,
                "end_lat": 30.0,
                "end_lon": -95.0,
            },
        )

    assert response.status_code == 422


def test_create_route_not_found(client: TestClient) -> None:
    """Test route creation when no route found."""
    with patch(
        "app.api.routes.routes.RouteService.calculate_and_save_route",
        side_effect=OSRMNotFoundError("No route found"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/routes/",
            json={
                "start_lat": 32.7767,
                "start_lon": -96.7970,
                "end_lat": 29.7604,
                "end_lon": -95.3698,
            },
        )

    assert response.status_code == 404
    content = response.json()
    assert "No route found" in content["detail"]


def test_create_route_timeout(client: TestClient) -> None:
    """Test route creation with timeout."""
    with patch(
        "app.api.routes.routes.RouteService.calculate_and_save_route",
        side_effect=OSRMTimeoutError("OSRM request timeout"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/routes/",
            json={
                "start_lat": 32.7767,
                "start_lon": -96.7970,
                "end_lat": 29.7604,
                "end_lon": -95.3698,
            },
        )

    assert response.status_code == 504


def test_create_route_server_error(client: TestClient) -> None:
    """Test route creation with server error."""
    with patch(
        "app.api.routes.routes.RouteService.calculate_and_save_route",
        side_effect=OSRMServerError("OSRM server error: 503"),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/routes/",
            json={
                "start_lat": 32.7767,
                "start_lon": -96.7970,
                "end_lat": 29.7604,
                "end_lon": -95.3698,
            },
        )

    assert response.status_code == 503

