from __future__ import annotations

from datetime import date

from db.base import Base

from sqlalchemy import Date, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesPersonalInformation(Base):
    __tablename__ = "employees_personal_information"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_hire: Mapped[date] = mapped_column(Date, nullable=False)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees_cnp.cnp"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="personal_information")
