from flask import Blueprint, request, jsonify, abort
from db.session import async_session

# Import your updated schemas and models here
from api.schemas.employees_salary_schema import EmployeesSalarySchema
from db.models.employees_salary_model import EmployeesSalary

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
        salary_valid = EmployeesSalarySchema.model_validate({
            "month": data["month"],
            "year": data["year"],
            "salary": data["salary"],
            "bonus": data["bonus"],
            "work": data["work"],
            "vacation": data["vacation"],
            "employeeId": data["cnp"]
        })
        salary_obj = EmployeesSalary(**salary_valid.model_dump())
        session.add(salary_obj)
        await session.commit()
        return jsonify({"Message": "Successful creation of salary"}), 201

@salary_bp.route("/salary/<int:salary_id>", methods=["GET"])
async def get_salary(salary_id):
    async with async_session() as session:
        salary_obj = await session.get(EmployeesSalary, salary_id)
        if not salary_obj:
            abort(404, "Salary not found")
        return jsonify(EmployeesSalarySchema.model_validate(dict(salary_obj.__dict__)).model_dump())

@salary_bp.route("/salary/<int:salary_id>", methods=["PUT"])
async def update_salary(salary_id):
    data = request.get_json()
    allowed_fields = {"salary", "bonus", "work", "vacation"}
    if set(data.keys()) != allowed_fields:
        abort(400, "Only salary, bonus, work, and vacation can be updated")
    async with async_session() as session:
        salary_obj = await session.get(EmployeesSalary, salary_id)
        if not salary_obj:
            abort(404, "Salary not found")
        for k in allowed_fields:
            setattr(salary_obj, k, data[k])
        EmployeesSalarySchema.model_validate(dict(salary_obj.__dict__))
        await session.commit()
        return jsonify({"salary_id": salary_id})
