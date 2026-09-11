"""Route service - business logic for route calculation and storage."""

import json
import logging
from typing import Any

from sqlmodel import Session

from app import crud
from app.infrastructure.osrm import OSRMClient, RouteResponse
from app.models import Route, RouteGeometry, RoutePublic

logger = logging.getLogger(__name__)

# Conversion constants
METERS_PER_MILE = 1609.344
SECONDS_PER_HOUR = 3600


class RouteService:
    """Service for route calculation and storage."""

    def __init__(self, osrm_client: OSRMClient | None = None) -> None:
        """Initialize route service.

        Args:
            osrm_client: OSRM client instance (optional, will create if not provided)
        """
        self.osrm_client = osrm_client or OSRMClient()

    async def calculate_and_save_route(
        self,
        session: Session,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
    ) -> RoutePublic:
        """Calculate route and save to database.

        Args:
            session: Database session
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Ending latitude
            end_lon: Ending longitude

        Returns:
            RoutePublic with saved route data

        Raises:
            OSRMException: If route calculation fails
        """
        logger.info(
            f"Starting route calculation from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})"
        )

        # Get route from OSRM
        osrm_response = await self.osrm_client.get_route(
            start_lat, start_lon, end_lat, end_lon
        )

        logger.info(
            f"Route received: {osrm_response.distance_meters}m in {osrm_response.duration_seconds}s"
        )

        # Calculate derived values
        distance_miles = self._meters_to_miles(osrm_response.distance_meters)
        duration_hours = self._seconds_to_hours(osrm_response.duration_seconds)

        logger.debug(f"Converted: {distance_miles:.2f} miles, {duration_hours:.2f} hours")

        # Build WKT geometry from GeoJSON
        wkt_geometry = None
        geojson_str = None
        if osrm_response.geometry:
            geojson_str = json.dumps({
                "type": osrm_response.geometry.type,
                "coordinates": osrm_response.geometry.coordinates,
            })
            wkt_geometry = self._geojson_to_wkt(osrm_response.geometry)

        # Save to database
        route = crud.create_route(
            session=session,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            distance_meters=osrm_response.distance_meters,
            duration_seconds=osrm_response.duration_seconds,
            geometry_wkt=wkt_geometry,
            geometry_geojson=geojson_str,
        )

        logger.info(f"Route saved to database with ID: {route.id}")

        # Build response
        return self._route_to_public(route, osrm_response.geometry)

    @staticmethod
    def _meters_to_miles(meters: float) -> float:
        """Convert meters to miles.

        Args:
            meters: Distance in meters

        Returns:
            Distance in miles
        """
        return meters / METERS_PER_MILE

    @staticmethod
    def _seconds_to_hours(seconds: float) -> float:
        """Convert seconds to hours.

        Args:
            seconds: Duration in seconds

        Returns:
            Duration in hours
        """
        return seconds / SECONDS_PER_HOUR

    @staticmethod
    def _geojson_to_wkt(geometry: RouteGeometry) -> str:
        """Convert GeoJSON geometry to WKT format for PostGIS.

        Args:
            geometry: RouteGeometry object

        Returns:
            WKT representation
        """
        if geometry.type != "LineString":
            raise ValueError(f"Unsupported geometry type: {geometry.type}")

        # Build WKT LineString
        coords = ", ".join(
            f"{lon} {lat}" for lat, lon in [(lat, lon) for lon, lat in geometry.coordinates]
        )
        return f"LINESTRING({coords})"

    @staticmethod
    def _route_to_public(
        route: Route, geometry: RouteGeometry | None = None
    ) -> RoutePublic:
        """Convert Route model to RoutePublic.

        Args:
            route: Route database model
            geometry: Optional RouteGeometry

        Returns:
            RoutePublic response
        """
        return RoutePublic(
            id=route.id,
            start_lat=route.start_lat,
            start_lon=route.start_lon,
            end_lat=route.end_lat,
            end_lon=route.end_lon,
            distance_meters=route.distance_meters,
            duration_seconds=route.duration_seconds,
            created_at=route.created_at,
            geometry=geometry,
        )

    async def get_route(self, session: Session, route_id: str) -> RoutePublic | None:
        """Get route by ID.

        Args:
            session: Database session
            route_id: Route UUID

        Returns:
            RoutePublic or None if not found
        """
        route = crud.get_route(session=session, route_id=route_id)
        if not route:
            return None

        # Parse geometry if available
        geometry = None
        if route.geometry_geojson:
            try:
                geom_data = json.loads(route.geometry_geojson)
                geometry = RouteGeometry(**geom_data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse geometry JSON: {e}")

        return self._route_to_public(route, geometry)




