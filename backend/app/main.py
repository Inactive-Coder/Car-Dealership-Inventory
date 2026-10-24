"""ASGI application entry point. Feature routes will be added in the TDD phase."""

from fastapi import FastAPI

app = FastAPI(
    title="Car Dealership Inventory API",
    version="0.1.0",
    description="API contract: ../docs/api-contract.yaml",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Basic process health; database readiness will be added with DB integration."""
    return {"status": "ok"}
