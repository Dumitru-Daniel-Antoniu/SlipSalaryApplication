from __future__ import annotations

from db.base import Base

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EmployeesEmail(Base):
    __tablename__ = "employees_email"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees_cnp.cnp"), nullable=False)

    employee: Mapped["EmployeesCNP"] = relationship(back_populates="email_information")