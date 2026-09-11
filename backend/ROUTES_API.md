"""API Routes Endpoint Usage Guide

## Endpoint: POST /api/v1/routes

### Description
Calculate a route between two coordinates using OSRM (Open Source Routing Machine).
The route geometry is stored in PostGIS and returned in GeoJSON format.

### Request
```json
{
  "start_lat": 32.7767,
  "start_lon": -96.7970,
  "end_lat": 29.7604,
  "end_lon": -95.3698
}
```

### Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "start_lat": 32.7767,
  "start_lon": -96.7970,
  "end_lat": 29.7604,
  "end_lon": -95.3698,
  "distance_meters": 385742.4,
  "duration_seconds": 13982.1,
  "created_at": "2026-09-10T00:00:00",
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [-96.7970, 32.7767],
      [-96.5, 32.5],
      [-95.3698, 29.7604]
    ]
  }
}
```

### Error Responses

#### 422 Unprocessable Entity
Invalid coordinates (latitude not in [-90, 90] or longitude not in [-180, 180])

#### 404 Not Found
No route found between coordinates

#### 503 Service Unavailable
OSRM service is unavailable or returned server error

#### 504 Gateway Timeout
OSRM request timed out

## Architecture

### Layers

1. **API Layer** (`app/api/routes/routes.py`)
   - HTTP endpoint definition
   - Request/Response models
   - Error handling

2. **Service Layer** (`app/services/routes.py`)
   - Business logic for route calculation
   - Coordinate validation
   - Distance/time unit conversion
   - Database operations

3. **Infrastructure Layer** (`app/infrastructure/osrm.py`)
   - OSRM client implementation
   - HTTP communication
   - Response parsing

4. **Repository Layer** (`app/crud.py`)
   - Database operations
   - GeoAlchemy2 geometry handling

5. **Models** (`app/models.py`)
   - SQLModel ORM definition
   - Pydantic schemas

### Database
- **Table**: `route`
- **Geometry Storage**: PostGIS `LineString` with SRID 4326
- **Indexes**: Spatial index on `route_geometry`, regular index on `created_at`

## Configuration

Set in `.env` or environment variables:
- `OSRM_BASE_URL`: OSRM service URL (default: https://router.project-osrm.org)

## Testing

All functionality is covered by tests:
- Unit tests for OSRM client
- Unit tests for route service
- Integration tests for CRUD operations
- API tests for endpoint

Run tests:
```bash
pytest tests/
```

## Implementation Notes

- Uses async/await for OSRM HTTP requests
- GeoAlchemy2 for PostGIS integration
- WKTElement for geometry storage
- GeoJSON for geometry API responses
- Proper error handling with specific exceptions
- Comprehensive logging
"""

