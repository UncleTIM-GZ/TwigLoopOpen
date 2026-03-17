"""Twig Loop Core API entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from shared_config import AppSettings
from shared_events import connect_nats, disconnect_nats
from shared_observability import setup_telemetry
from shared_schemas import ApiResponse

from app.api.v1.router import v1_router
from app.exceptions import AppError
from app.observability import TraceContextMiddleware

settings = AppSettings()
setup_telemetry(service_name="core-api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle — connect/disconnect NATS."""
    await connect_nats()
    yield
    await disconnect_nats()


app = FastAPI(
    title="Twig Loop Core API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom application errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": exc.message, "meta": None},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Unify HTTPException responses to standard envelope format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": exc.detail, "meta": None},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions (SQLAlchemy, etc.)."""
    import logging

    logging.getLogger(__name__).exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"success": False, "data": None, "error": "Internal server error", "meta": None},
    )


app.add_middleware(TraceContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(v1_router)


@app.get("/health")  # type: ignore[untyped-decorator]
async def health_check() -> ApiResponse[dict[str, str]]:
    """Health check endpoint."""
    return ApiResponse(success=True, data={"status": "ok"})


@app.get("/metrics")  # type: ignore[untyped-decorator]
async def get_metrics() -> dict:
    """Internal metrics snapshot for operator use."""
    from app.metrics import metrics

    return metrics.snapshot()
