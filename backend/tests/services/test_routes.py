"""Unit tests for route service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session

from app.infrastructure.osrm import (
    OSRMClient,
    OSRMInvalidCoordinatesError,
    RouteResponse,
)
from app.models import RouteGeometry
from app.services.routes import RouteService


class TestRouteService:
    """Test cases for route service."""

    def test_meters_to_miles_conversion(self) -> None:
        """Test meters to miles conversion."""
        # 1 mile = 1609.344 meters
        assert RouteService._meters_to_miles(1609.344) == pytest.approx(1.0, rel=1e-5)
        assert RouteService._meters_to_miles(385742.4) == pytest.approx(239.69, rel=1e-2)

    def test_seconds_to_hours_conversion(self) -> None:
        """Test seconds to hours conversion."""
        # 1 hour = 3600 seconds
        assert RouteService._seconds_to_hours(3600) == pytest.approx(1.0, rel=1e-5)
        assert RouteService._seconds_to_hours(13982.1) == pytest.approx(3.884, rel=1e-2)

    def test_geojson_to_wkt_conversion(self) -> None:
        """Test GeoJSON to WKT conversion."""
        geometry = RouteGeometry(
            type="LineString",
            coordinates=[
                [-96.7970, 32.7767],
                [-95.3698, 29.7604],
            ],
        )

        wkt = RouteService._geojson_to_wkt(geometry)

        # WKT format: LINESTRING(lon lat, lon lat, ...)
        assert wkt.startswith("LINESTRING(")
        assert wkt.endswith(")")
        assert "-96.7970 32.7767" in wkt
        assert "-95.3698 29.7604" in wkt

    def test_geojson_to_wkt_unsupported_type(self) -> None:
        """Test GeoJSON to WKT with unsupported geometry type."""
        geometry = RouteGeometry(
            type="Point",  # type: ignore
            coordinates=[[-96.7970, 32.7767]],
        )

        with pytest.raises(ValueError, match="Unsupported geometry type"):
            RouteService._geojson_to_wkt(geometry)

    @pytest.mark.asyncio
    async def test_calculate_and_save_route_success(self, db: Session) -> None:
        """Test successful route calculation and saving."""
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

        # Mock OSRM client
        mock_client = AsyncMock(spec=OSRMClient)
        mock_client.get_route.return_value = mock_osrm_response

        # Create service with mock client
        service = RouteService(osrm_client=mock_client)

        # Call service
        result = await service.calculate_and_save_route(
            session=db,
            start_lat=32.7767,
            start_lon=-96.7970,
            end_lat=29.7604,
            end_lon=-95.3698,
        )

        # Verify result
        assert result.start_lat == 32.7767
        assert result.start_lon == -96.7970
        assert result.end_lat == 29.7604
        assert result.end_lon == -95.3698
        assert result.distance_meters == 385742.4
        assert result.duration_seconds == 13982.1
        assert result.geometry is not None

    @pytest.mark.asyncio
    async def test_calculate_and_save_route_osrm_error(self, db: Session) -> None:
        """Test route calculation with OSRM error."""
        # Mock OSRM client to raise error
        mock_client = AsyncMock(spec=OSRMClient)
        mock_client.get_route.side_effect = OSRMInvalidCoordinatesError(
            "Invalid coordinates"
        )

        # Create service
        service = RouteService(osrm_client=mock_client)

        # Call service and expect error
        with pytest.raises(OSRMInvalidCoordinatesError):
            await service.calculate_and_save_route(
                session=db,
                start_lat=32.7767,
                start_lon=-96.7970,
                end_lat=29.7604,
                end_lon=-95.3698,
            )

