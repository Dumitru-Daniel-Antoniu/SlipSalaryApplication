from __future__ import annotations

from db.base import Base

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesName(Base):
    __tablename__ = "employees_name"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees_cnp.cnp"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="name_information")
