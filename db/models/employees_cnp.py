from __future__ import annotations

from db.session import db

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesCNP(db.Model):
    __tablename__ = "employees_cnp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CNP: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)

    names: Mapped["EmployeesName"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    personal_information: Mapped["EmployeesPersonalInformation"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    administrative_information: Mapped["EmployeesAdministrativeInformation"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
