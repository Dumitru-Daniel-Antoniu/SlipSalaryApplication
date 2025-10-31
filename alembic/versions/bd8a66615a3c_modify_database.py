"""Modify database

Revision ID: bd8a66615a3c
Revises: 2bba27286f84
Create Date: 2025-10-31 10:14:40.744893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd8a66615a3c'
down_revision: Union[str, Sequence[str], None] = '2bba27286f84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employees_cnp",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False, autoincrement=True),
        sa.Column("cnp", sa.String(length=13), nullable=False, unique=True),
    )

    op.create_table(
        "employees_name",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("surname", sa.String(length=50), nullable=False),
        sa.Column("employee_id", sa.String(length=13), sa.ForeignKey("employees_cnp.cnp"), nullable=False),
    )

    op.create_table(
        "employees_email",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=50), nullable=False, unique=True),
        sa.Column("employee_id", sa.String(length=13), sa.ForeignKey("employees_cnp.cnp"), nullable=False),
    )

    op.create_table(
        "employees_personal_information",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("position", sa.String(length=50), nullable=False),
        sa.Column("department", sa.String(length=50), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("date_of_hire", sa.Date(), nullable=False),
        sa.Column("employee_id", sa.String(length=13), sa.ForeignKey("employees_cnp.cnp"), nullable=False),
    )

    op.create_table(
        "employees_salary",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("salary", sa.Float(), nullable=False),
        sa.Column("bonus", sa.Float(), nullable=False),
        sa.Column("work", sa.Integer(), nullable=False),
        sa.Column("vacation", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.String(length=13), sa.ForeignKey("employees_cnp.cnp"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("employees_salary")
    op.drop_table("employees_personal_information")
    op.drop_table("employees_email")
    op.drop_table("employees_name")
    op.drop_table("employees_cnp")
