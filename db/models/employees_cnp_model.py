from __future__ import annotations

from db.base import Base

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List


class EmployeesCNP(Base):
    __tablename__ = "employees_cnp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    cnp: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)

    name_information: Mapped["EmployeesName"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    personal_information: Mapped["EmployeesPersonalInformation"] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    salary_information: Mapped[List["EmployeesSalary"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
