from __future__ import annotations

from datetime import date

from db.session import db

from sqlalchemy import Date, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesPersonalInformation(db.Model):
    __tablename__ = "employees_personal_information"

    position: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_hire: Mapped[date] = mapped_column(Date, nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_name.id"), nullable=False)

    employee: Mapped["EmployeesName"] = relationship(back_populates="personal_information")
