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
    work: Mapped[int] = mapped_column(Integer, nullable=False)
    vacation: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_cnp.cnp"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="salary_information")
