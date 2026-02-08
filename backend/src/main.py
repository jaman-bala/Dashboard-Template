import sys
import uvicorn
from fastapi import FastAPI, Request
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from pathlib import Path

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)

sys.path.append(str(Path(__file__).parent.parent))

from src.core.init import redis_manager
from src.apps.api.auth import router as router_auth
from src.apps.api.health import router as router_health
from src.core.config import settings
from src.core.utils.logging_config import get_logger
from src.core.utils.validation_handlers import validation_exception_handler
from src.apps.middleware.rate_limiting import RateLimitMiddleware
from src.apps.middleware.exception_handler import ExceptionHandlerMiddleware

logger = get_logger(__name__)

app_name = settings.PROJECT_NAME

registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "fastapi_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "http_status", "app_name"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "fastapi_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint", "app_name"],
    registry=registry,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.close()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.MODE != "PROD" else None,  # Swagger in DEV/test
    redoc_url="/redoc" if settings.MODE != "PROD" else None,  # ReDoc in DEV/test
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Dashboard Template API with enhanced security",
    openapi_tags=[
        {
            "name": "Authorization and authentication",
            "description": "Operations with authentication and user management",
        },
        {
            "name": "Health",
            "description": "Health check endpoints",
        },
        {
            "name": "Tickets",
            "description": "Operations with tickets",
        },
    ],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

security = HTTPBearer()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    with REQUEST_LATENCY.labels(
        method=method, endpoint=endpoint, app_name=app_name
    ).time():
        response = await call_next(request)

    status_code = response.status_code
    REQUEST_COUNT.labels(
        method=method, endpoint=endpoint, http_status=status_code, app_name=app_name
    ).inc()

    return response


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


app.mount(
    "/static/avatars", StaticFiles(directory=settings.LINK_IMAGES), name="avatars"
)
app.mount(
    "/static/photo", StaticFiles(directory=settings.LINK_UPLOAD_PHOTO), name="photo"
)
app.mount(
    "/static/upload-files",
    StaticFiles(directory=settings.LINK_UPLOAD_FILES),
    name="upload-files",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# API Versioning - all routes under /api/v1
API_V1_PREFIX = "/api/v1"
app.include_router(router_health, prefix=API_V1_PREFIX)
app.include_router(router_auth, prefix=API_V1_PREFIX)


@app.get("/", response_class=JSONResponse)
async def read_root():
    return {"message": "backend 🏆"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
