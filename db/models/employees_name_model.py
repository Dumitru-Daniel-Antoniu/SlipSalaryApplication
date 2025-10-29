from __future__ import annotations

from db.session import db

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesName(db.Model):
    __tablename__ = "employees_name"

    cnp: Mapped[str] = mapped_column(String(13), primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)

    personal_information: Mapped["EmployeesPersonalInformation"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    administrative_information: Mapped["EmployeesAdministrativeInformation"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
