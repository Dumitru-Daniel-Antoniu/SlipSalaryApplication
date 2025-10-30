from flask import Blueprint, request, jsonify, abort
from db.session import async_session

from api.schemas.employees_cnp_schema import EmployeesCNPSchema
from api.schemas.employees_name_schema import EmployeesNameSchema
from api.schemas.employees_personal_information_schema import EmployeesPersonalInformationSchema
from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation

employee_bp = Blueprint("employee", __name__)

def validate_employee_request(data):
    required_fields = {"cnp", "name", "surname", "position", "department", "dateOfBirth", "dateOfHire"}
    if set(data.keys()) != required_fields:
        abort(400, "Invalid employee request structure")
    return data

@employee_bp.route("/employees", methods=["POST"])
async def create_employee():
    data = validate_employee_request(request.get_json())
    async with async_session() as session:
        # Validate and create CNP
        cnp_valid = EmployeesCNPSchema.model_validate({"cnp": data["cnp"], "id": None})
        cnp_obj = EmployeesCNP(cnp=data["cnp"])
        session.add(cnp_obj)
        await session.flush()

        # Validate and create name
        name_valid = EmployeesNameSchema.model_validate({
            "name": data["name"],
            "surname": data["surname"],
            "employeeId": cnp_obj.cnp
        })
        name_obj = EmployeesName(**name_valid.model_dump())
        session.add(name_obj)

        # Validate and create personal info
        personal_valid = EmployeesPersonalInformationSchema.model_validate({
            "position": data["position"],
            "department": data["department"],
            "dateOfBirth": data["dateOfBirth"],
            "dateOfHire": data["dateOfHire"],
            "employeeId": cnp_obj.cnp
        })
        personal_obj = EmployeesPersonalInformation(**personal_valid.model_dump())
        session.add(personal_obj)

        await session.commit()
        return jsonify({"Message": "Successful creation of the employee"}), 201

@employee_bp.route("/employees/<string:cnp>", methods=["GET"])
async def get_employee(cnp):
    async with async_session() as session:
        cnp_obj = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.cnp == cnp)
        )
        cnp_row = cnp_obj.fetchone()
        if not cnp_row:
            abort(404, "Employee not found")

        name_obj = await session.execute(
            EmployeesName.__table__.select().where(EmployeesName.employee_id == cnp)
        )
        name_row = name_obj.fetchone()

        personal_obj = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(EmployeesPersonalInformation.employee_id == cnp)
        )
        personal_row = personal_obj.fetchone()

        return jsonify({
            "cnp": dict(cnp_row) if cnp_row else {},
            "name": dict(name_row) if name_row else {},
            "personal": dict(personal_row) if personal_row else {}
        })

@employee_bp.route("/employees/<string:cnp>", methods=["PUT"])
async def update_employee(cnp):
    data = request.get_json()
    allowed_fields = {"position", "department"}
    if set(data.keys()) != allowed_fields:
        abort(400, "Only position and department can be updated")
    async with async_session() as session:
        personal_obj = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(EmployeesPersonalInformation.employee_id == cnp)
        )
        personal_row = personal_obj.fetchone()
        if not personal_row:
            abort(404, "Employee personal info not found")
        for k, v in data.items():
            setattr(personal_row, k, v)
        EmployeesPersonalInformationSchema.model_validate(dict(personal_row))
        await session.commit()
        return jsonify({"cnp": cnp})

@employee_bp.route("/employees/<string:cnp>", methods=["DELETE"])
async def delete_employee(cnp):
    async with async_session() as session:
        cnp_obj = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.cnp == cnp)
        )
        cnp_row = cnp_obj.fetchone()
        if not cnp_row:
            abort(404, "Employee not found")
        await session.delete(cnp_row)
        await session.commit()
        return "", 204
