"""Remove password default

Revision ID: 1c1be3a0fa13
Revises: dd052185230e
Create Date: 2025-11-06 15:30:03.155639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1c1be3a0fa13'
down_revision: Union[str, Sequence[str], None] = 'dd052185230e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "employees_name",
        "password",
        existing_type=sa.String(length=128),
        server_default=None,
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "employees_name",
        "password",
        existing_type=sa.String(length=128),
        server_default=sa.text("'password'"),
        existing_nullable=False,
    )
