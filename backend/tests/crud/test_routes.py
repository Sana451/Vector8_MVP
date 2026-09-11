"""Tests for route CRUD operations."""

from sqlmodel import Session

from app import crud


def test_create_route(db: Session) -> None:
    """Test creating a route."""
    route = crud.create_route(
        session=db,
        start_lat=32.7767,
        start_lon=-96.7970,
        end_lat=29.7604,
        end_lon=-95.3698,
        distance_meters=385742.4,
        duration_seconds=13982.1,
        geometry_geojson='{"type":"LineString","coordinates":[[-96.7970,32.7767],[-95.3698,29.7604]]}',
    )

    assert route.start_lat == 32.7767
    assert route.start_lon == -96.7970
    assert route.end_lat == 29.7604
    assert route.end_lon == -95.3698
    assert route.distance_meters == 385742.4
    assert route.duration_seconds == 13982.1
    assert route.geometry_geojson is not None
    assert route.created_at is not None


def test_get_route(db: Session) -> None:
    """Test getting route by ID."""
    # Create a route
    created_route = crud.create_route(
        session=db,
        start_lat=32.7767,
        start_lon=-96.7970,
        end_lat=29.7604,
        end_lon=-95.3698,
        distance_meters=385742.4,
        duration_seconds=13982.1,
    )

    # Get route
    retrieved_route = crud.get_route(session=db, route_id=str(created_route.id))

    assert retrieved_route is not None
    assert retrieved_route.id == created_route.id
    assert retrieved_route.start_lat == created_route.start_lat


def test_get_route_not_found(db: Session) -> None:
    """Test getting non-existent route."""
    route = crud.get_route(session=db, route_id="00000000-0000-0000-0000-000000000000")

    assert route is None


def test_get_route_invalid_id(db: Session) -> None:
    """Test getting route with invalid ID format."""
    route = crud.get_route(session=db, route_id="invalid-id")

    assert route is None


