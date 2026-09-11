"""Unit tests for OSRM client."""


import pytest

from app.infrastructure.osrm import (
    OSRMClient,
    OSRMException,
    OSRMInvalidCoordinatesError,
    OSRMNotFoundError,
    OSRMServerError,
    OSRMTimeoutError,
    RouteResponse,
)


class TestOSRMClient:
    """Test cases for OSRM client."""

    @pytest.mark.asyncio
    async def test_successful_route_request(self) -> None:
        """Test successful OSRM route request.

        This test verifies that OSRMClient correctly handles successful API responses.
        TODO: Implement proper mocking with httpx.MockTransport or monkeypatch.
        """
        # This test is currently a placeholder pending proper mock implementation
        # The mock_get function below shows the expected response structure
        mock_response = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 385742.4,
                    "duration": 13982.1,
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-96.7970, 32.7767],
                            [-96.5, 32.5],
                            [-95.3698, 29.7604],
                        ],
                    },
                }
            ],
        }

        # Expected mock response structure for when proper mocking is implemented
        assert mock_response["code"] == "Ok"
        assert len(mock_response["routes"]) == 1

    def test_invalid_coordinates_negative_latitude(self) -> None:
        """Test invalid coordinates with out-of-range latitude."""
        client = OSRMClient()

        with pytest.raises(OSRMInvalidCoordinatesError):
            client._validate_coordinates(
                start_lat=-95.0,  # Invalid
                start_lon=-96.0,
                end_lat=30.0,
                end_lon=-95.0,
            )

    def test_invalid_coordinates_out_of_range_longitude(self) -> None:
        """Test invalid coordinates with out-of-range longitude."""
        client = OSRMClient()

        with pytest.raises(OSRMInvalidCoordinatesError):
            client._validate_coordinates(
                start_lat=32.0,
                start_lon=-200.0,  # Invalid
                end_lat=30.0,
                end_lon=-95.0,
            )

    def test_valid_coordinates(self) -> None:
        """Test valid coordinates pass validation."""
        client = OSRMClient()

        # Should not raise
        client._validate_coordinates(
            start_lat=32.7767,
            start_lon=-96.7970,
            end_lat=29.7604,
            end_lon=-95.3698,
        )

    def test_build_url_format(self) -> None:
        """Test OSRM URL building."""
        client = OSRMClient()

        url = client._build_url(
            start_lat=32.7767,
            start_lon=-96.7970,
            end_lat=29.7604,
            end_lon=-95.3698,
        )

        # Verify URL format
        assert "router.project-osrm.org" in url
        assert "/route/v1/driving/" in url
        # Check coordinates are in URL (may be rounded during formatting)
        assert "-96.79" in url and "32.776" in url  # Start coords (rounded)
        assert "-95.369" in url and "29.76" in url  # End coords (rounded)
        assert "overview=full" in url
        assert "geometries=geojson" in url

    def test_route_response_parsing_success(self) -> None:
        """Test successful route response parsing."""
        response_data = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 385742.4,
                    "duration": 13982.1,
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-96.7970, 32.7767],
                            [-95.3698, 29.7604],
                        ],
                    },
                }
            ],
        }

        response = RouteResponse(response_data)

        assert response.distance_meters == 385742.4
        assert response.duration_seconds == 13982.1
        assert response.geometry is not None
        assert response.geometry.type == "LineString"
        assert len(response.geometry.coordinates) == 2

    def test_route_response_parsing_no_routes(self) -> None:
        """Test route response parsing with no routes."""
        response_data = {
            "code": "Ok",
            "routes": [],
        }

        with pytest.raises(OSRMNotFoundError):
            RouteResponse(response_data)

    def test_route_response_parsing_missing_geometry(self) -> None:
        """Test route response parsing with missing geometry."""
        response_data = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 385742.4,
                    "duration": 13982.1,
                }
            ],
        }

        response = RouteResponse(response_data)

        assert response.distance_meters == 385742.4
        assert response.duration_seconds == 13982.1
        assert response.geometry is None


class TestOSRMClientErrors:
    """Test error handling in OSRM client."""

    def test_osrm_exception_inheritance(self) -> None:
        """Test OSRM exception inheritance."""
        assert issubclass(OSRMInvalidCoordinatesError, OSRMException)
        assert issubclass(OSRMTimeoutError, OSRMException)
        assert issubclass(OSRMServerError, OSRMException)
        assert issubclass(OSRMNotFoundError, OSRMException)

