"""Add password

Revision ID: dd052185230e
Revises: afc464f3b872
Create Date: 2025-11-05 23:29:11.342046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dd052185230e'
down_revision: Union[str, Sequence[str], None] = 'afc464f3b872'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'employees_name',
        sa.Column(
            'password',
            sa.String(128),
            nullable=False,
            server_default='password'
        )
    )


def downgrade() -> None:
    op.drop_table('employees_cnp')
    op.drop_table('idempotency_keys')
    op.drop_table('employees_name')
    op.drop_table('employees_salary')
    op.drop_table('employees_email')
    op.drop_table('employees_personal_information')