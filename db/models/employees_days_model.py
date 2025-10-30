from __future__ import annotations

from db.base import Base

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesDays(Base):
    __tablename__ = "employees_days"

    work: Mapped[int] = mapped_column(Integer, nullable=False)
    vacation: Mapped[int] = mapped_column(Integer, nullable=False)
    month_id: Mapped[int] = mapped_column(ForeignKey("employees_administrative_information.month_id"), nullable=False)

    employee: Mapped["EmployeesAdministrativeInformation"] = relationship(back_populates="days")
