import uuid
from typing import Any
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, Route, User, UserCreate, UserUpdate
def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user
# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user
def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
# Route CRUD operations
def create_route(
    *,
    session: Session,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    distance_meters: float,
    duration_seconds: float,
    geometry_wkt: str | None = None,
    geometry_geojson: str | None = None,
) -> Route:
    """Create a new route.
    Args:
        session: Database session
        start_lat: Starting latitude
        start_lon: Starting longitude
        end_lat: Ending latitude
        end_lon: Ending longitude
        distance_meters: Distance in meters
        duration_seconds: Duration in seconds
        geometry_wkt: WKT geometry for PostGIS storage
        geometry_geojson: GeoJSON geometry as string
    Returns:
        Created Route object
    """
    db_route = Route(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        distance_meters=distance_meters,
        duration_seconds=duration_seconds,
    )
    # Set geometry if provided
    if geometry_wkt:
        # Store WKT geometry as text
        db_route.route_geometry = geometry_wkt
    if geometry_geojson:
        db_route.geometry_geojson = geometry_geojson
    session.add(db_route)
    session.commit()
    session.refresh(db_route)
    return db_route
def get_route(*, session: Session, route_id: str) -> Route | None:
    """Get route by ID.
    Args:
        session: Database session
        route_id: Route UUID as string
    Returns:
        Route object or None if not found
    """
    try:
        uuid_id = uuid.UUID(route_id)
        statement = select(Route).where(Route.id == uuid_id)
        return session.exec(statement).first()
    except ValueError:
        return None
