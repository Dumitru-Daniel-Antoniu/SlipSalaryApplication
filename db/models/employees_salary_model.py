from __future__ import annotations

from db.base import Base

from sqlalchemy import ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesSalary(Base):
    __tablename__ = "employees_salary"

    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    bonus = Mapped[float] = mapped_column(Float, nullable=False)
    month_id: Mapped[int] = mapped_column(ForeignKey("employees_administrative_information.month_id"), nullable=False)

    employee: Mapped["EmployeesAdministrativeInformation"] = relationship(back_populates="salary")
