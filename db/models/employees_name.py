from __future__ import annotations

from db.session import db

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesName(db.Model):
    __tablename__ = "employees_name"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_cnp.id"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="names")
