from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique operation ID for OpenAPI documentation.

    Uses the first tag if available, otherwise falls back to route name.
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Configure CORS - allow all origins in development, specific origin in production
cors_origins = ["*"] if settings.FASTAPI_ENV == "development" else [settings.FRONTEND_HOST]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount frontend static files
if FRONTEND_DIR.exists():
    # Mount assets directory
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

    # Serve index.html for root path
    @app.get("/")
    async def serve_root() -> FileResponse:
        """Serve index.html for root path."""
        return FileResponse(FRONTEND_DIR / "index.html")

    # Serve index.html for client-side routing (all other paths)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve SPA with fallback to index.html for client-side routes."""
        file_path = FRONTEND_DIR / full_path

        # If file exists and is not a directory, serve it
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for client-side routing
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    import warnings
    warnings.warn(f"Frontend directory not found at {FRONTEND_DIR}", stacklevel=2)
