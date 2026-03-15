"""AI Assist Service entrypoint."""

from fastapi import FastAPI
from shared_observability import setup_telemetry
from shared_schemas import ApiResponse

setup_telemetry(service_name="ai-assist-service")

app = FastAPI(title="Twig Loop AI Assist Service", version="0.1.0")


@app.get("/health", response_model=ApiResponse[dict])
async def health_check() -> ApiResponse[dict]:
    """Health check endpoint."""
    return ApiResponse(success=True, data={"status": "ok"})
