from __future__ import annotations

from db.session import db

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List


class EmployeesAdministrativeInformation(db.Model):
    __tablename__ = "employees_administrative_information"

    month_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_cnp.id"), nullable=False)

    employee: Mapped["EmployeesName"] = relationship(back_populates="administrative_information")

    salary: Mapped[List["EmployeesSalary"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    days: Mapped[List["EmployeesDays"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
