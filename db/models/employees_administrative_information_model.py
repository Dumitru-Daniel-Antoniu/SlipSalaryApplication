from __future__ import annotations

from db.base import Base

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List


class EmployeesAdministrativeInformation(Base):
    __tablename__ = "employees_administrative_information"

    month_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_cnp.cnp"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="administrative_information")

    salary: Mapped[List["EmployeesSalary"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    days: Mapped[List["EmployeesDays"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
