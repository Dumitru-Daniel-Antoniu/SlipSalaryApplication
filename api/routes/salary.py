from flask import Blueprint, request, jsonify, abort
from db.session import async_session

from api.schemas.employees_salary_schema import EmployeesSalarySchema
from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_salary_model import EmployeesSalary

from sqlalchemy import select


salary_bp = Blueprint("salary", __name__)


def validate_salary_days_request(data):
    required_fields = {"month", "year", "salary", "bonus", "work", "vacation", "cnp"}
    if set(data.keys()) != required_fields:
        abort(400, "Invalid salary/days request structure")
    return data


@salary_bp.route("/salary", methods=["POST"])
async def create_salary():
    data = validate_salary_days_request(request.get_json())
    async with async_session() as session:
        salary_data = EmployeesSalarySchema.model_validate({
            "month": data["month"],
            "year": data["year"],
            "salary": data["salary"],
            "bonus": data["bonus"],
            "work": data["work"],
            "vacation": data["vacation"],
            "employeeId": data["cnp"]
        })

        salary = EmployeesSalary(**salary_data.model_dump())
        session.add(salary)
        await session.commit()

        return jsonify({"Message": "Successful creation of salary"}), 201


@salary_bp.route("/salary/<int:id>", methods=["GET"])
async def get_salary(id):
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if month is None or year is None:
        abort(400, "Month and year query parameters are required")

    async with async_session() as session:
        cnp_data = await session.get(EmployeesCNP, id)

        if not cnp_data:
            abort(404, "Employee not found")

        cnp = cnp_data.cnp
        salary_data = await session.execute(
            select(EmployeesSalary).where(
                EmployeesSalary.employeeId == cnp,
                EmployeesSalary.month == month,
                EmployeesSalary.year == year
            )
        )
        salary = salary_data.scalar_one_or_none()

        if not salary:
            abort(404, "Salary for given month and year not found")

        return jsonify(EmployeesSalarySchema.model_validate(dict(salary.__dict__)).model_dump())


@salary_bp.route("/salary/<int:id>", methods=["PUT"])
async def update_salary(id):
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if month is None or year is None:
        abort(400, "Month and year query parameters are required")

    data = request.get_json()
    allowed_fields = {"salary", "bonus", "work", "vacation"}

    if set(data.keys()) != allowed_fields:
        abort(400, "Only salary, bonus, work, and vacation can be updated")

    async with async_session() as session:
        cnp_data = await session.get(EmployeesCNP, id)

        if not cnp_data:
            abort(404, "Employee not found")

        cnp = cnp_data.cnp
        salary_data = await session.execute(
            select(EmployeesSalary).where(
                EmployeesSalary.employeeId == cnp,
                EmployeesSalary.month == month,
                EmployeesSalary.year == year
            )
        )

        salary = salary_data.scalar_one_or_none()

        if not salary:
            abort(404, "Salary for given month and year not found")

        for k in allowed_fields:
            setattr(salary, k, data[k])

        EmployeesSalarySchema.model_validate(dict(salary.__dict__))
        await session.commit()
        return jsonify({"salary_id": salary.id})
