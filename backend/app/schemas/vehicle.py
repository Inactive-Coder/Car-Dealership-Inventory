from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    quantity: int = Field(ge=0, strict=True)

    @field_validator("make", "model", "category", mode="before")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class VehicleCreate(VehicleFields):
    pass


class VehicleUpdate(VehicleFields):
    pass


class VehicleResponse(VehicleFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class VehiclePage(BaseModel):
    items: list[VehicleResponse]
    offset: int
    limit: int
    total: int


class RestockRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1, strict=True)


class VehicleSearch(BaseModel):
    make: str | None = Field(default=None, min_length=1)
    model: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1)
    min_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    max_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)

