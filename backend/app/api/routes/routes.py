"""Routes for route calculation."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import SessionDep
from app.infrastructure.osrm import (
    OSRMException,
    OSRMInvalidCoordinatesError,
    OSRMNotFoundError,
    OSRMServerError,
    OSRMTimeoutError,
)
from app.models import RoutePublic
from app.services.routes import RouteService

router = APIRouter(prefix="/routes", tags=["routes"])


class RouteRequest(BaseModel):
    """Request model with start and end coordinates."""
    start_lat: float = Field(ge=-90, le=90, description="Starting latitude")
    start_lon: float = Field(ge=-180, le=180, description="Starting longitude")
    end_lat: float = Field(ge=-90, le=90, description="Ending latitude")
    end_lon: float = Field(ge=-180, le=180, description="Ending longitude")

    class Config:
        json_schema_extra = {
            "example": {
                "start_lat": 32.7767,
                "start_lon": -96.7970,
                "end_lat": 29.7604,
                "end_lon": -95.3698,
            }
        }


@router.post("/", response_model=RoutePublic, status_code=status.HTTP_201_CREATED)
async def create_route(
    *, session: SessionDep, route_request: RouteRequest
) -> Any:
    """Calculate route between two coordinates.

    Args:
        session: Database session
        route_request: Request with start and end coordinates

    Returns:
        RoutePublic with calculated route details

    Raises:
        422: Invalid coordinates
        503: OSRM service unavailable
        504: OSRM request timeout
        404: No route found
    """
    service = RouteService()

    try:
        route = await service.calculate_and_save_route(
            session=session,
            start_lat=route_request.start_lat,
            start_lon=route_request.start_lon,
            end_lat=route_request.end_lat,
            end_lon=route_request.end_lon,
        )
        return route
    except OSRMInvalidCoordinatesError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except OSRMNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OSRMTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(e),
        )
    except OSRMServerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except OSRMException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )



