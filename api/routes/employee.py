from api.schemas.employees_administrative_information_schema import EmployeesAdministrativeInformationSchema
from api.schemas.employees_name_schema import EmployeesNameSchema
from api.schemas.employees_personal_information_schema import EmployeesPersonalInformationSchema

from db.models.employees_administrative_information_model import EmployeesAdministrativeInformation
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation
from db.session import async_session

from flask import Blueprint, request, jsonify, abort


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
        name_valid = EmployeesNameSchema.model_validate({
            "cnp": data["cnp"],
            "name": data["name"],
            "surname": data["surname"]
        })

        name = EmployeesName(**name_valid.model_dump())
        session.add(name)
        await session.flush()


        personal_valid = EmployeesPersonalInformationSchema.model_validate({
            "position": data["position"],
            "department": data["department"],
            "dateOfBirth": data["dateOfBirth"],
            "dateOfHire": data["dateOfHire"],
            "employeeId": data["cnp"]
        })
        personal = EmployeesPersonalInformation(**personal_valid.model_dump())
        session.add(personal)

        await session.commit()
        return jsonify({"Message": "Successful creation of the employee"}), 201


@employee_bp.route("/employees/<string:cnp>", methods=["GET"])
async def get_employee(cnp):
    async with async_session() as session:
        name = await session.get(EmployeesName, cnp)
        if not name:
            abort(404, "Employee not found")
        personal = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(
                EmployeesPersonalInformation.employee_id == cnp
            )
        )
        personal_row = personal.fetchone()
        admin = await session.execute(
            EmployeesAdministrativeInformation.__table__.select().where(
                EmployeesAdministrativeInformation.employee_id == cnp
            )
        )
        admin_row = admin.fetchone()
        return jsonify({
            "name": EmployeesNameSchema.model_validate(dict(name.__dict__)).model_dump(),
            "personal": EmployeesPersonalInformationSchema.model_validate(dict(personal_row) if personal_row else {}).model_dump(),
            "admin": EmployeesAdministrativeInformationSchema.model_validate(dict(admin_row) if admin_row else {}).model_dump()
        })


@employee_bp.route("/employees/<string:cnp>", methods=["PUT"])
async def update_employee(cnp):
    data = request.get_json()
    allowed_fields = {"position", "department"}
    if set(data.keys()) != allowed_fields:
        abort(400, "Only position and department can be updated")
    async with async_session() as session:
        personal = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(
                EmployeesPersonalInformation.employee_id == cnp
            )
        )
        personal_row = personal.fetchone()
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
        name = await session.get(EmployeesName, cnp)
        if not name:
            abort(404, "Employee not found")
        await session.delete(name)
        await session.commit()
        return "", 204
