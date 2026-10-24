"""ASGI application entry point."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import AuthenticationError, AuthorizationError, get_current_user, require_admin
from app.core.database import get_db
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth import DuplicateEmailError, InvalidCredentialsError, authenticate_user, register_user
from app.schemas.vehicle import RestockRequest, VehicleCreate, VehiclePage, VehicleResponse, VehicleSearch, VehicleUpdate
from app.services.vehicles import (
    OutOfStockError,
    VehicleNotFoundError,
    create_vehicle,
    delete_vehicle,
    list_vehicles,
    purchase_one,
    restock_vehicle,
    search_vehicles,
    update_vehicle,
)

app = FastAPI(
    title="Car Dealership Inventory API",
    version="0.1.0",
    description="API contract: ../docs/api-contract.yaml",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def auth_error(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


@app.exception_handler(DuplicateEmailError)
async def duplicate_email_handler(_: Request, __: DuplicateEmailError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"error": {"code": "duplicate_email", "message": "An account with this email already exists."}},
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(_: Request, __: InvalidCredentialsError) -> JSONResponse:
    return auth_error("invalid_credentials", "Email or password is incorrect.", 401)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(_: Request, __: AuthenticationError) -> JSONResponse:
    return auth_error("unauthorized", "Valid authentication credentials are required.", 401)


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(_: Request, __: AuthorizationError) -> JSONResponse:
    return auth_error("forbidden", "Administrator permissions are required.", 403)


@app.exception_handler(VehicleNotFoundError)
async def vehicle_not_found_handler(_: Request, __: VehicleNotFoundError) -> JSONResponse:
    return auth_error("not_found", "Vehicle was not found.", 404)


@app.exception_handler(OutOfStockError)
async def out_of_stock_handler(_: Request, __: OutOfStockError) -> JSONResponse:
    return auth_error("out_of_stock", "Vehicle is currently out of stock.", 409)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"field": ".".join(str(part) for part in error["loc"] if part != "body"), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Request validation failed.", "details": details}},
    )


@app.post("/api/auth/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
def register(payload: RegisterRequest, session: Session = Depends(get_db)) -> UserResponse:
    user = register_user(payload, session)
    # SQLAlchemy client-side defaults are normally assigned during INSERT; set the
    # public fields explicitly as well, which keeps the service easy to unit test.
    if user.id is None:
        user.id = uuid4()
    if user.created_at is None:
        user.created_at = datetime.now(timezone.utc)
    return UserResponse.model_validate(user)


@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(payload: LoginRequest, session: Session = Depends(get_db)) -> TokenResponse:
    user, token, expires_in = authenticate_user(payload, session)
    if user.id is None:
        user.id = uuid4()
    if user.created_at is None:
        user.created_at = datetime.now(timezone.utc)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@app.get("/api/vehicles", response_model=VehiclePage, tags=["Vehicles"])
def get_vehicles(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: object = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> VehiclePage:
    items, total = list_vehicles(session, offset, limit)
    return VehiclePage(items=items, offset=offset, limit=limit, total=total)


@app.get("/api/vehicles/search", response_model=VehiclePage, tags=["Vehicles"])
def search_inventory(
    make: str | None = Query(default=None, min_length=1, max_length=100),
    model: str | None = Query(default=None, min_length=1, max_length=100),
    category: str | None = Query(default=None, min_length=1, max_length=50),
    min_price: Decimal | None = Query(default=None, ge=0, max_digits=12, decimal_places=2),
    max_price: Decimal | None = Query(default=None, ge=0, max_digits=12, decimal_places=2),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: object = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> VehiclePage:
    if min_price is not None and max_price is not None and min_price > max_price:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": [{"field": "min_price", "message": "must be less than or equal to max_price"}],
                }
            },
        )
    filters = VehicleSearch(make=make, model=model, category=category, min_price=min_price, max_price=max_price)
    items, total = search_vehicles(session, filters, offset, limit)
    return VehiclePage(items=items, offset=offset, limit=limit, total=total)


@app.post("/api/vehicles", response_model=VehicleResponse, status_code=201, tags=["Vehicles"])
def add_vehicle(
    payload: VehicleCreate,
    _: object = Depends(require_admin),
    session: Session = Depends(get_db),
) -> VehicleResponse:
    return create_vehicle(payload, session)


@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleResponse, tags=["Vehicles"])
def edit_vehicle(
    vehicle_id: UUID,
    payload: VehicleUpdate,
    _: object = Depends(require_admin),
    session: Session = Depends(get_db),
) -> VehicleResponse:
    return update_vehicle(vehicle_id, payload, session)


@app.delete("/api/vehicles/{vehicle_id}", status_code=204, tags=["Vehicles"])
def remove_vehicle(
    vehicle_id: UUID,
    _: object = Depends(require_admin),
    session: Session = Depends(get_db),
) -> Response:
    delete_vehicle(vehicle_id, session)
    return Response(status_code=204)


@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=VehicleResponse, tags=["Vehicles"])
def purchase_vehicle(
    vehicle_id: UUID,
    _: object = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> VehicleResponse:
    return purchase_one(vehicle_id, session)


@app.post("/api/vehicles/{vehicle_id}/restock", response_model=VehicleResponse, tags=["Vehicles"])
def restock(
    vehicle_id: UUID,
    payload: RestockRequest,
    _: object = Depends(require_admin),
    session: Session = Depends(get_db),
) -> VehicleResponse:
    return restock_vehicle(vehicle_id, payload.quantity, session)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Basic process health; database readiness will be added with DB integration."""
    return {"status": "ok"}
