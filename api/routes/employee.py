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
        cnp_data = EmployeesCNPSchema.model_validate({
            "cnp": data["cnp"],
            "id": None
        })

        cnp = EmployeesCNP(cnp=data["cnp"])
        session.add(cnp)
        await session.flush()

        name_data = EmployeesNameSchema.model_validate({
            "name": data["name"],
            "surname": data["surname"],
            "employeeId": cnp.cnp
        })
        name = EmployeesName(**name_data.model_dump())
        session.add(name)

        personal_data = EmployeesPersonalInformationSchema.model_validate({
            "position": data["position"],
            "department": data["department"],
            "dateOfBirth": data["dateOfBirth"],
            "dateOfHire": data["dateOfHire"],
            "employeeId": cnp.cnp
        })
        personal = EmployeesPersonalInformation(**personal_data.model_dump())
        session.add(personal)

        await session.commit()
        return jsonify({"Message": "Successful creation of the employee"}), 201


@employee_bp.route("/employees/<int:id>", methods=["GET"])
async def get_employee(id):
    async with async_session() as session:
        cnp_data = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.id == id)
        )

        cnp = cnp_data.fetchone()
        if not cnp:
            abort(404, "Employee not found")

        name_data = await session.execute(
            EmployeesName.__table__.select().where(EmployeesName.employee_id == cnp.cnp)
        )
        name = name_data.fetchone()

        personal_data = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(EmployeesPersonalInformation.employee_id == cnp.cnp)
        )
        personal = personal_data.fetchone()

        return jsonify({
            "cnp": cnp.cnp,
            "name": dict(name),
            "personal": dict(personal)
        })


@employee_bp.route("/employees/<int:id>", methods=["PUT"])
async def update_employee(id):
    data = request.get_json()
    allowed_fields = {"position", "department"}

    if set(data.keys()) != allowed_fields:
        abort(400, "Only position and department can be updated")

    async with async_session() as session:
        cnp_data = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.id == id)
        )

        cnp = cnp_data.fetchone()
        if not cnp:
            abort(404, "Employee not found")

        personal_data = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(EmployeesPersonalInformation.employee_id == cnp.cnp)
        )
        personal = personal_data.fetchone()

        if not personal:
            abort(404, "Employee personal info not found")

        for k, v in data.items():
            setattr(personal, k, v)

        EmployeesPersonalInformationSchema.model_validate(dict(personal))
        await session.commit()
        return jsonify()


@employee_bp.route("/employees/<int:id>", methods=["DELETE"])
async def delete_employee(id):
    async with async_session() as session:
        cnp_data = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.id == id)
        )
        cnp = cnp_data.fetchone()

        if not cnp:
            abort(404, "Employee not found")

        await session.delete(cnp)
        await session.commit()
        return "", 204
