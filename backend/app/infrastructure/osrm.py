"""OSRM (Open Source Routing Machine) client for route calculation."""

import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.models import RouteGeometry

logger = logging.getLogger(__name__)


class OSRMException(Exception):
    """Base exception for OSRM client errors."""
    pass


class OSRMTimeoutError(OSRMException):
    """OSRM request timeout."""
    pass


class OSRMServerError(OSRMException):
    """OSRM server error."""
    pass


class OSRMNotFoundError(OSRMException):
    """Route not found."""
    pass


class OSRMInvalidCoordinatesError(OSRMException):
    """Invalid coordinates provided."""
    pass


class RouteResponse:
    """Response from OSRM route endpoint."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize response from OSRM data."""
        self.raw_data = data
        self.distance_meters: float = 0.0
        self.duration_seconds: float = 0.0
        self.geometry: RouteGeometry | None = None

        self._parse_response()

    def _parse_response(self) -> None:
        """Parse OSRM response."""
        if "routes" not in self.raw_data or not self.raw_data["routes"]:
            raise OSRMNotFoundError("No route found in OSRM response")

        route = self.raw_data["routes"][0]

        # Extract distance and duration
        self.distance_meters = float(route.get("distance", 0))
        self.duration_seconds = float(route.get("duration", 0))

        # Extract geometry
        if "geometry" in route:
            geom_data = route["geometry"]
            if isinstance(geom_data, dict):
                # GeoJSON format
                if geom_data.get("type") == "LineString":
                    self.geometry = RouteGeometry(
                        type="LineString",
                        coordinates=geom_data.get("coordinates", []),
                    )
            elif isinstance(geom_data, str):
                # Encoded polyline format (should not happen with geometries=geojson)
                logger.warning("Received encoded geometry instead of GeoJSON")
                self.geometry = None
        else:
            logger.warning("No geometry in OSRM response")
            self.geometry = None


class OSRMClient:
    """OSRM routing client."""

    def __init__(self, base_url: str = settings.OSRM_BASE_URL) -> None:
        """Initialize OSRM client.

        Args:
            base_url: OSRM base URL
        """
        self.base_url = base_url.rstrip("/")

    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
    ) -> RouteResponse:
        """Get route from OSRM.

        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Ending latitude
            end_lon: Ending longitude

        Returns:
            RouteResponse with route details

        Raises:
            OSRMInvalidCoordinatesError: If coordinates are invalid
            OSRMTimeoutError: If request times out
            OSRMServerError: If server returns error
            OSRMNotFoundError: If no route found
        """
        # Validate coordinates
        self._validate_coordinates(start_lat, start_lon, end_lat, end_lon)

        # Build URL
        url = self._build_url(start_lat, start_lon, end_lat, end_lon)

        logger.info(
            f"Requesting route from OSRM: ({start_lat}, {start_lon}) -> ({end_lat}, {end_lon})"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)

                logger.debug(f"OSRM response status: {response.status_code}")

                if response.status_code == 400:
                    raise OSRMInvalidCoordinatesError(
                        f"Invalid coordinates: {response.text}"
                    )
                elif response.status_code == 404:
                    raise OSRMNotFoundError("No route found")
                elif response.status_code >= 500:
                    raise OSRMServerError(
                        f"OSRM server error: {response.status_code}"
                    )
                elif response.status_code != 200:
                    raise OSRMException(
                        f"Unexpected status code: {response.status_code}"
                    )

                data = response.json()

                # Check OSRM response code
                if data.get("code") != "Ok":
                    error_msg = data.get("message", "Unknown error")
                    raise OSRMException(f"OSRM error: {error_msg}")

                logger.info("Successfully received route from OSRM")
                return RouteResponse(data)

        except httpx.TimeoutException as e:
            logger.error(f"OSRM request timeout: {e}")
            raise OSRMTimeoutError("OSRM request timeout") from e
        except httpx.HTTPError as e:
            logger.error(f"OSRM HTTP error: {e}")
            raise OSRMServerError(f"OSRM HTTP error: {e}") from e

    def _validate_coordinates(
        self, start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> None:
        """Validate coordinates.

        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Ending latitude
            end_lon: Ending longitude

        Raises:
            OSRMInvalidCoordinatesError: If coordinates are invalid
        """
        # Check latitude range
        if not (-90 <= start_lat <= 90):
            raise OSRMInvalidCoordinatesError(
                f"Invalid start latitude: {start_lat}"
            )
        if not (-90 <= end_lat <= 90):
            raise OSRMInvalidCoordinatesError(f"Invalid end latitude: {end_lat}")

        # Check longitude range
        if not (-180 <= start_lon <= 180):
            raise OSRMInvalidCoordinatesError(
                f"Invalid start longitude: {start_lon}"
            )
        if not (-180 <= end_lon <= 180):
            raise OSRMInvalidCoordinatesError(f"Invalid end longitude: {end_lon}")

    def _build_url(
        self, start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> str:
        """Build OSRM API URL.

        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Ending latitude
            end_lon: Ending longitude

        Returns:
            Full URL for OSRM request
        """
        # OSRM expects lon,lat format
        url = (
            f"{self.base_url}/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}"
            f"?overview=full&geometries=geojson"
        )
        return url

