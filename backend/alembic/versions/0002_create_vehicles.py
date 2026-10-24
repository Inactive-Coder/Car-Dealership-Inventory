"""Create vehicles table.

Revision ID: 0002_create_vehicles
Revises: 0001_create_users
Create Date: 2026-10-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_vehicles"
down_revision: Union[str, None] = "0001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("make", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_vehicles_price_nonnegative"),
        sa.CheckConstraint("quantity >= 0", name="ck_vehicles_quantity_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vehicles_make", "vehicles", ["make"], unique=False)
    op.create_index("ix_vehicles_model", "vehicles", ["model"], unique=False)
    op.create_index("ix_vehicles_category", "vehicles", ["category"], unique=False)
    op.create_index("ix_vehicles_price", "vehicles", ["price"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vehicles_price", table_name="vehicles")
    op.drop_index("ix_vehicles_category", table_name="vehicles")
    op.drop_index("ix_vehicles_model", table_name="vehicles")
    op.drop_index("ix_vehicles_make", table_name="vehicles")
    op.drop_table("vehicles")
