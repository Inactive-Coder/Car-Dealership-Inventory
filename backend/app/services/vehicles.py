from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleSearch, VehicleUpdate


class VehicleNotFoundError(Exception):
    pass


class OutOfStockError(Exception):
    pass


def list_vehicles(session: Session, offset: int, limit: int) -> tuple[list[Vehicle], int]:
    items = list(session.scalars(select(Vehicle).order_by(Vehicle.make, Vehicle.model, Vehicle.id).offset(offset).limit(limit)).all())
    total = session.scalar(select(func.count()).select_from(Vehicle)) or 0
    return items, total


def search_vehicles(session: Session, filters: VehicleSearch, offset: int, limit: int) -> tuple[list[Vehicle], int]:
    statement = select(Vehicle)
    count_statement = select(func.count()).select_from(Vehicle)
    if filters.make is not None:
        criterion = Vehicle.make.ilike(f"%{filters.make.strip()}%")
        statement, count_statement = statement.where(criterion), count_statement.where(criterion)
    if filters.model is not None:
        criterion = Vehicle.model.ilike(f"%{filters.model.strip()}%")
        statement, count_statement = statement.where(criterion), count_statement.where(criterion)
    if filters.category is not None:
        criterion = func.lower(Vehicle.category) == filters.category.strip().lower()
        statement, count_statement = statement.where(criterion), count_statement.where(criterion)
    if filters.min_price is not None:
        criterion = Vehicle.price >= filters.min_price
        statement, count_statement = statement.where(criterion), count_statement.where(criterion)
    if filters.max_price is not None:
        criterion = Vehicle.price <= filters.max_price
        statement, count_statement = statement.where(criterion), count_statement.where(criterion)
    items = list(session.scalars(statement.order_by(Vehicle.make, Vehicle.model, Vehicle.id).offset(offset).limit(limit)).all())
    total = session.scalar(count_statement) or 0
    return items, total


def create_vehicle(payload: VehicleCreate, session: Session) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


def update_vehicle(vehicle_id: UUID, payload: VehicleUpdate, session: Session) -> Vehicle:
    vehicle = session.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))
    if vehicle is None:
        raise VehicleNotFoundError
    for field, value in payload.model_dump().items():
        setattr(vehicle, field, value)
    vehicle.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(vehicle)
    return vehicle


def delete_vehicle(vehicle_id: UUID, session: Session) -> None:
    vehicle = session.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))
    if vehicle is None:
        raise VehicleNotFoundError
    session.delete(vehicle)
    session.commit()


def purchase_one(vehicle_id: UUID, session: Session) -> Vehicle:
    statement = (
        update(Vehicle)
        .where(Vehicle.id == vehicle_id, Vehicle.quantity > 0)
        .values(quantity=Vehicle.quantity - 1, updated_at=datetime.now(timezone.utc))
        .returning(Vehicle)
    )
    vehicle = session.execute(statement).scalar_one_or_none()
    if vehicle is None:
        exists = session.scalar(select(Vehicle.id).where(Vehicle.id == vehicle_id))
        if exists is None:
            raise VehicleNotFoundError
        raise OutOfStockError
    session.commit()
    return vehicle


def restock_vehicle(vehicle_id: UUID, amount: int, session: Session) -> Vehicle:
    statement = (
        update(Vehicle)
        .where(Vehicle.id == vehicle_id)
        .values(quantity=Vehicle.quantity + amount, updated_at=datetime.now(timezone.utc))
        .returning(Vehicle)
    )
    vehicle = session.execute(statement).scalar_one_or_none()
    if vehicle is None:
        raise VehicleNotFoundError
    session.commit()
    return vehicle
