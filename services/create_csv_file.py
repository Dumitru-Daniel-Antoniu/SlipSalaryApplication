import os
import pandas as pd
import uuid

from datetime import datetime

from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation
from db.models.employees_salary_model import EmployeesSalary
from db.session import async_session

from flask import abort

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, OperationalError, SQLAlchemyError

from werkzeug.exceptions import HTTPException


async def generate_csv_data(employee_id: int) -> str:
    if not isinstance(employee_id, int):
        abort(400, "Employee ID must be an integer")

    async with async_session() as session:
        try:
            cnp_data = await session.get(EmployeesCNP, employee_id)
            if cnp_data is None:
                abort(404, "Employee not found")

            personal_data = await session.execute(
                select(EmployeesPersonalInformation).where(
                    EmployeesPersonalInformation.employee_id == cnp_data.cnp
                )
            )

            personal = personal_data.scalar_one_or_none()
            if not personal:
                abort(404, "Personal information not found")
            if personal.position != "Manager":
                abort(403, "Only managers can generate a CSV file")

            department = personal.department

            now = datetime.now()
            month = now.month
            year = now.year

            statement = (
                select(
                    EmployeesName.name,
                    EmployeesName.surname,
                    EmployeesSalary.salary,
                    EmployeesSalary.work,
                    EmployeesSalary.vacation,
                    EmployeesSalary.bonus
                )
                .select_from(EmployeesCNP)
                .join(EmployeesName, EmployeesName.employee_id == EmployeesCNP.cnp)
                .join(EmployeesPersonalInformation, EmployeesPersonalInformation.employee_id == EmployeesCNP.cnp)
                .join(EmployeesSalary, EmployeesSalary.employee_id == EmployeesCNP.cnp)
                .where(
                    EmployeesPersonalInformation.department == department,
                    EmployeesSalary.month == month,
                    EmployeesSalary.year == year
                )
            )

            result = await session.execute(statement)
            rows = result.fetchall()

            df = pd.DataFrame(rows, columns=["Name", "Surname", "Salary", "Work Days", "Vacation Days", "Bonus"])

            filename = f"Employees_department_status_{department}_{year}_{month}_{uuid.uuid4().hex}.csv"
            filepath = os.path.join("temporary/csv", filename)
            df.to_csv(filepath)

            return filepath
        except OperationalError:
            abort(500, "Database connection error or deadlock")
        except SQLAlchemyError:
            abort(500, "General database error")
        except MultipleResultsFound:
            abort(500, "Multiple records of personal information for an employee")
        except HTTPException as e:
            raise e
        except Exception:
            abort(500, "Unexpected error")
