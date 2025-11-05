"""Add a new table

Revision ID: afc464f3b872
Revises: bd8a66615a3c
Create Date: 2025-11-05 17:31:12.514438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afc464f3b872'
down_revision: Union[str, Sequence[str], None] = 'bd8a66615a3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("endpoint", sa.String(length=128), nullable=False),
        sa.Column("response_data", sa.JSON(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("key", "endpoint", name="uq_key_endpoint"),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
