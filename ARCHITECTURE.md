# Vector8 Architecture

## 🏗️ Общее описание

Vector8 - это приложение для оптимизации маршрутов с полнофункциональной архитектурой, разделенной на чистые слои с четкой разделением ответственности.

```
┌─────────────────────────────────────┐
│     Frontend (React + Vite)         │ - SPA, Leaflet map, React Router
├─────────────────────────────────────┤
│     API Gateway (Traefik proxy)     │ - Routing, SSL/TLS, load balancing
├─────────────────────────────────────┤
│     FastAPI Application             │ - HTTP layer, request validation
│  ┌─────────────────────────────────┐│
│  │    API Routes (endpoints)        ││ - /api/v1/routes, /api/v1/items, etc
│  ├─────────────────────────────────┐│
│  │    Dependency Injection (deps)   ││ - Authentication, database session
│  ├─────────────────────────────────┐│
│  │    Service Layer (business logic)││ - RouteService, ItemService, etc
│  ├─────────────────────────────────┐│
│  │    Infrastructure Layer          ││ - OSRM client, utilities
│  ├─────────────────────────────────┐│
│  │    CRUD Layer (data operations)  ││ - create_user, get_item, etc
│  └─────────────────────────────────┘│
├─────────────────────────────────────┤
│     Database (PostgreSQL + PostGIS)  │ - User, Item, Route tables
├─────────────────────────────────────┤
│     External Services (OSRM)         │ - Route calculation
└─────────────────────────────────────┘
```

---

## 📁 Структура проекта

```
Vector8/
├── backend/                          # FastAPI приложение
│   ├── app/
│   │   ├── api/                      # HTTP API слой
│   │   │   ├── deps.py              # Dependency injection (JWT, DB session)
│   │   │   ├── main.py              # Агрегирование маршрутов
│   │   │   └── routes/
│   │   │       ├── items.py         # Item CRUD endpoints
│   │   │       ├── login.py         # Authentication endpoints
│   │   │       ├── users.py         # User CRUD endpoints
│   │   │       ├── routes.py        # Route calculation endpoints
│   │   │       └── private.py       # Protected user endpoints
│   │   │
│   │   ├── core/                    # Core utilities
│   │   │   ├── config.py            # Pydantic settings
│   │   │   ├── db.py                # Database connection
│   │   │   └── security.py          # JWT, password hashing
│   │   │
│   │   ├── services/                # Business logic слой
│   │   │   ├── routes.py            # Route calculation service
│   │   │   └── items.py             # Item service
│   │   │
│   │   ├── infrastructure/          # External integrations
│   │   │   ├── osrm.py              # OSRM routing client
│   │   │   └── exceptions.py        # Custom exceptions
│   │   │
│   │   ├── crud.py                  # Data access layer
│   │   ├── models.py                # SQLModel database models
│   │   └── main.py                  # FastAPI app initialization
│   │
│   ├── tests/                       # Тестирование
│   │   ├── api/                    # Endpoint tests
│   │   ├── services/               # Service logic tests
│   │   ├── crud/                   # CRUD operation tests
│   │   ├── infrastructure/         # Integration tests
│   │   └── conftest.py             # Pytest fixtures
│   │
│   └── alembic/                    # Database migrations
│
├── frontend/                        # React приложение
│   ├── src/
│   │   ├── routes/                 # Page components
│   │   ├── components/             # Reusable UI components
│   │   ├── hooks/                  # Custom React hooks
│   │   └── client/                 # Generated API client
│   └── tests/                      # Playwright e2e tests
│
└── deployment/                     # Infrastructure configs
    ├── compose.yml                 # Production compose
    └── compose.override.yml        # Development overrides
```

---

## 🔄 Data Flow

### Route Creation Request

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User sends POST /api/v1/routes/                           │
│    { start_lat, start_lon, end_lat, end_lon }                │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. FastAPI Router (api/routes/routes.py)                     │
│    - Validates request (RouteRequest Pydantic model)         │
│    - Extracts current user from JWT token (deps.py)          │
│    - Gets database session (SessionDep)                      │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Service Layer (services/routes.py)                        │
│    - Validates coordinates via OSRMClient                    │
│    - Calls OSRM API for route calculation                    │
│    - Converts GeoJSON geometry to WKT format                 │
│    - Calculates distances and durations                      │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Infrastructure Layer (infrastructure/osrm.py)             │
│    - Makes HTTP call to router.project-osrm.org              │
│    - Handles errors (timeout, invalid coords, etc)           │
│    - Returns RouteResponse with geometry                     │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. CRUD Layer (crud.py)                                      │
│    - Saves Route object to database via SQLModel             │
│    - Stores geometry as GeoJSON text (PostGIS extension is    │
│      enabled on the DB, but this column is not yet a native   │
│      `geometry` type — see schema note below)                 │
│    - Returns created Route with ID                           │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Response                                                   │
│    - HTTP 200 with Route object containing:                  │
│      * distance_km, duration_minutes                         │
│      * geometry (GeoJSON for map display)                    │
│      * created_at timestamp                                  │
└──────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌─────────────────────────────────────────┐
│ 1. POST /api/v1/login/access-token      │
│    { username, password }               │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 2. core/security.py                     │
│    - verify_password (bcrypt/argon2)    │
│    - generate_jwt_token                 │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 3. Response                             │
│    { access_token, token_type: "bearer" }
└─────────────────────────────────────────┘
               
         Then for protected endpoints:
               ▼
┌─────────────────────────────────────────┐
│ 4. Request with Authorization header    │
│    Bearer <access_token>                │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 5. api/deps.py - get_current_user()     │
│    - Decode JWT token                   │
│    - Extract user_id from payload       │
│    - Fetch user from database           │
│    - Check if active                    │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 6. Route handler receives User object   │
│    Can access current_user.id, email    │
└─────────────────────────────────────────┘
```

---

## 🔌 Ключевые компоненты

### 1. API Layer (app/api/)

**Ответственность:** HTTP запрос → валидация → вызов сервиса

```python
@router.post("/routes/", response_model=RouteResponse)
async def create_route(
    route_request: RouteRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Create a new route calculation."""
    # 1. Request is already validated by Pydantic
    # 2. current_user injected via dependency
    # 3. session injected for database access
    route = await RouteService().calculate_and_save_route(...)
    return route
```

**Файлы:**
- `deps.py` - Dependency injection (JWT, database session)
- `main.py` - Aggregates all route modules
- `routes/` - Endpoint implementations

### 2. Service Layer (app/services/)

**Ответственность:** Бизнес логика, оркестрация компонентов

```python
class RouteService:
    async def calculate_and_save_route(
        self, 
        session: Session,
        start_lat: float, 
        start_lon: float,
        end_lat: float,
        end_lon: float
    ) -> Route:
        # 1. Call infrastructure to get route data
        route_response = await self.osrm_client.get_route(...)
        
        # 2. Transform data to database format
        geometry_wkt = self._geojson_to_wkt(route_response.geometry)
        
        # 3. Save to database
        route = crud.create_route(session, route_data)
        
        return route
```

**Файлы:**
- `routes.py` - Route calculation and storage
- `items.py` - Item management

### 3. Infrastructure Layer (app/infrastructure/)

**Ответственность:** Внешние интеграции, сетевые запросы

```python
class OSRMClient:
    """OSRM (Open Source Routing Machine) client.
    
    Communicates with router.project-osrm.org for route calculations.
    """
    
    async def get_route(self, start_lat, start_lon, end_lat, end_lon):
        # 1. Validate coordinates
        # 2. Build URL
        # 3. Make HTTP request
        # 4. Parse response
        # 5. Handle errors with custom exceptions
```

**Исключения:**
- `OSRMException` - базовый класс
- `OSRMInvalidCoordinatesError` - невалидные координаты
- `OSRMServerError` - ошибка сервера OSRM
- `OSRMTimeoutError` - timeout
- `OSRMNotFoundError` - маршрут не найден

### 4. CRUD Layer (app/crud.py)

**Ответственность:** Операции с БД

```python
def create_user(session: Session, user_create: UserCreate) -> User:
    """Create user in database."""
    db_obj = User.from_orm(user_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_route(session: Session, route_id: UUID) -> Route | None:
    """Fetch route by ID."""
    return session.get(Route, route_id)
```

### 5. Models (app/models.py)

**SQLModel** - комбинирует SQLAlchemy ORM и Pydantic валидацию

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Route(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    distance_meters: float
    duration_seconds: float
    geometry_geojson: str | None  # GeoJSON for map
    created_at: datetime
```

---

## 🔐 Security Architecture

### Password Security
```python
# core/security.py
def get_password_hash(password: str) -> str:
    # Uses argon2/bcrypt for hashing
    # ~200ms per hash (prevents brute force)
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Timing attack resistant comparison
```

### JWT Authentication
```
┌─────────────────────────────────────┐
│ User login                          │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ generate_jwt_token(user_id)         │
│ - Header: { "alg": "HS256" }        │
│ - Payload: { "sub": user_id }       │
│ - Signature: HMAC(secret)           │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ Return token to client              │
│ Expires after 24 hours              │
└─────────────────────────────────────┘
```

---

## 📊 Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOL DEFAULT TRUE,
    is_superuser BOOL DEFAULT FALSE,
    created_at TIMESTAMP WITH TZ
);

-- Items
CREATE TABLE item (
    id UUID PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    owner_id UUID FOREIGN KEY REFERENCES user(id),
    created_at TIMESTAMP WITH TZ
);

-- Routes (DB has the PostGIS extension enabled, but the columns below
-- are plain TEXT/FLOAT — no native `geometry` column is used yet)
CREATE TABLE route (
    id UUID PRIMARY KEY,
    start_lat FLOAT NOT NULL,
    start_lon FLOAT NOT NULL,
    end_lat FLOAT NOT NULL,
    end_lon FLOAT NOT NULL,
    distance_meters FLOAT NOT NULL,
    duration_seconds FLOAT NOT NULL,
    geometry_geojson TEXT,           -- GeoJSON LineString (actually populated)
    route_geometry TEXT,             -- reserved for a future native PostGIS
                                      -- geometry column; unused today
    created_at TIMESTAMP WITH TZ
);

CREATE INDEX ix_route_created_at ON route(created_at);
CREATE INDEX ix_route_geometry ON route USING GIST(route_geometry);
```

---

## 🚀 Deployment Architecture

### Development (compose.override.yml)
- Frontend served from Vite dev server
- Backend runs with uvicorn (no reload watcher)
- Database hot-reloads via Docker sync
- Mailpit for email testing

### Production (compose.yml)
- Frontend built and served by FastAPI
- Backend runs with fastapi run (multiple workers)
- Reverse proxy (Traefik) handles SSL/TLS
- Database requires manual backups

---

## 🔄 Request/Response Cycle

### Typical API Request

```
1. Browser/Client
   └─> GET /api/v1/items/?skip=0&limit=100

2. Traefik Reverse Proxy
   └─> Forward to FastAPI backend:8000

3. FastAPI Router Matching
   └─> Match to api/routes/items.py::get_items()

4. Dependency Injection
   └─> Inject: SessionDep (database), CurrentUser (JWT auth)

5. Request Handler
   └─> crud.get_items(session, skip=0, limit=100)

6. Database Query
   └─> SELECT * FROM item LIMIT 100 OFFSET 0

7. Response Serialization
   └─> ItemResponse[] via Pydantic

8. HTTP Response
   └─> 200 OK with JSON body

9. Frontend Rendering
   └─> React receives JSON and renders UI
```

---

## 🧪 Testing Strategy

### Unit Tests
- `tests/crud/` - Database operations
- `tests/services/` - Business logic with mocks
- `tests/infrastructure/` - External API clients

### Integration Tests
- `tests/api/` - Full endpoint testing with real DB

### E2E Tests
- `frontend/tests/` - Playwright browser automation

---

## ✅ Best Practices Implemented

- ✅ Type hints everywhere (strict mypy mode)
- ✅ Dependency injection for testability
- ✅ Separation of concerns (layers)
- ✅ Error handling with custom exceptions
- ✅ Database migrations (Alembic)
- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Pydantic validation
- ✅ Comprehensive logging
- ✅ Environment-based configuration

---

## 🚦 Next Steps for Production

1. Add rate limiting middleware
2. Implement caching layer (Redis)
3. Add request/response logging middleware
4. Setup monitoring (Sentry, Prometheus)
5. Add API versioning deprecation strategy
6. Implement API key authentication option
7. Add webhook support for async operations
8. Setup database read replicas

---

*Architecture Version: 1.0*

