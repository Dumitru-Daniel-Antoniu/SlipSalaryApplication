from api.schemas.employees_days_schema import EmployeesDaysSchema
from api.schemas.employees_salary_schema import EmployeesSalarySchema

from db.models.employees_administrative_information_model import EmployeesAdministrativeInformation
from db.models.employees_days_model import EmployeesDays
from db.models.employees_salary_model import EmployeesSalary
from db.session import async_session

from flask import Blueprint, request, jsonify, abort

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
        # Validate salary
        salary_valid = EmployeesSalarySchema.model_validate({
            "month": data["month"],
            "year": data["year"],
            "salary": data["salary"],
            "bonus": data["bonus"],
            "monthId": None  # will be set after flush
        })
        salary = EmployeesSalary(**salary_valid.model_dump())
        session.add(salary)
        await session.flush()

        # Validate days
        days_valid = EmployeesDaysSchema.model_validate({
            "work": data["work"],
            "vacation": data["vacation"],
            "monthId": salary.month_id
        })
        days = EmployeesDays(**days_valid.model_dump())
        session.add(days)

        # Administrative info
        admin = EmployeesAdministrativeInformation(month_id=salary.month_id, employee_id=data["cnp"])
        session.add(admin)

        await session.commit()
        return jsonify({"month_id": salary.month_id}), 201

@salary_bp.route("/salary/<int:month_id>", methods=["GET"])
async def get_salary(month_id):
    async with async_session() as session:
        salary = await session.get(EmployeesSalary, month_id)
        days = await session.get(EmployeesDays, month_id)
        if not salary or not days:
            abort(404, "Salary or days not found")
        return jsonify({
            "salary": EmployeesSalarySchema.model_validate(dict(salary.__dict__)).model_dump(),
            "days": EmployeesDaysSchema.model_validate(dict(days.__dict__)).model_dump()
        })

@salary_bp.route("/salary/<int:month_id>", methods=["PUT"])
async def update_salary(month_id):
    data = request.get_json()
    allowed_fields = {"salary", "bonus", "work", "vacation"}
    if set(data.keys()) != allowed_fields:
        abort(400, "Only salary, bonus, work, and vacation can be updated")
    async with async_session() as session:
        salary = await session.get(EmployeesSalary, month_id)
        days = await session.get(EmployeesDays, month_id)
        if not salary or not days:
            abort(404, "Salary or days not found")
        for k in ["salary", "bonus"]:
            setattr(salary, k, data[k])
        for k in ["work", "vacation"]:
            setattr(days, k, data[k])
        EmployeesSalarySchema.model_validate(dict(salary.__dict__))
        EmployeesDaysSchema.model_validate(dict(days.__dict__))
        await session.commit()
        return jsonify({"month_id": month_id})
