import logging
import jwt

from flask import Blueprint, request, jsonify, abort
from db.session import async_session
from sqlalchemy.exc import SQLAlchemyError
from api.schemas.employees_cnp_schema import EmployeesCNPSchema
from api.schemas.employees_name_schema import EmployeesNameSchema
from api.schemas.employees_personal_information_schema import EmployeesPersonalInformationSchema
from api.schemas.employees_email_schema import EmployeesEmailSchema
from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation
from db.models.employees_email_model import EmployeesEmail
from db.models.employees_salary_model import EmployeesSalary

from werkzeug.exceptions import HTTPException

from sqlalchemy import select

logging.basicConfig(level=logging.INFO)

employee_bp = Blueprint("employee", __name__)


def validate_employee_request(data):
    required_fields = {"cnp", "name", "surname", "password", "position", "department", "dateOfBirth", "dateOfHire", "email"}
    if set(data.keys()) != required_fields:
        abort(400, "Invalid employee request structure")
    return data


@employee_bp.route("/employees/department", methods=["GET"])
async def employees_in_manager_department():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401, "Missing or invalid Authorization header")

    token = auth.split(" ", 1)[1].strip()
    try:
        # decode without signature verification just to extract claims
        # if you have the secret/public key available, prefer verification:
        payload = jwt.decode(token, options={"verify_signature": False})
        logging.info("Decoded JWT payload: %s", payload)   
    except Exception:
        abort(401, "Invalid token")

    department = payload.get("sub").get("department")
    if not department:
        logging.warning("Department claim not present in token")

        abort(400, "Department claim not present in token")

    async with async_session() as session:
        # join personal info, name and email to build employee list
        try:

            stmt = (
                select(EmployeesPersonalInformation)
                .where(EmployeesPersonalInformation.department == department)
            )
            logging.info("Executing statement: %s", stmt)
            rows = await session.execute(stmt)
            personal_rows = rows.scalars().all()

            results = []
            logging.info("Fetched %d employees in department %s", len(personal_rows), department)
            for pr in personal_rows:

                emp_id = pr.employee_id
                logging.info("Fetching data for employee_id: %s", emp_id)
                # get name
                name_row = await session.execute(
                    select(EmployeesName).where(EmployeesName.employee_id == emp_id)
                )
                name = name_row.scalar_one_or_none()


                # get email
                email_row = await session.execute(
                    select(EmployeesEmail).where(EmployeesEmail.employee_id == emp_id)
                )
                email = email_row.scalar_one_or_none()
                results.append({
                    "employee_id": emp_id,
                    "name": name.name,
                    "surname": name.surname,
                    "email": email.email,
                })

            logging.info("Returning %d employees for department %s", len(results), department)
            return jsonify(results)
        except Exception as e:
            logging.exception("Failed to fetch employees by department")
            abort(500, "Failed to fetch employees")


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
        name_dict = dict(name._mapping) if name else None

        personal_data = await session.execute(
            EmployeesPersonalInformation.__table__.select().where(EmployeesPersonalInformation.employee_id == cnp.cnp)
        )
        personal = personal_data.fetchone()
        personal_dict = dict(personal._mapping) if personal else None

        email_data = await session.execute(
            EmployeesEmail.__table__.select().where(EmployeesEmail.employee_id == cnp.cnp)
        )
        email = email_data.fetchone()
        email_dict = dict(email._mapping) if email else None

        return jsonify({
            "cnp": cnp.cnp,
            "name": name_dict,
            "personal": personal_dict,
            "email": email_dict
        })


@employee_bp.route("/employees/<int:id>", methods=["PUT"])
async def update_employee(id):
    data = request.get_json()
    allowed_fields = {"position", "department", "email"}
    if not allowed_fields.issuperset(data.keys()):
        abort(400, "Only position, department, and email can be updated")

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

        updated = False
        for k in {"position", "department"} & data.keys():
            setattr(personal, k, data[k])
            updated = True
        if updated:
            await session.execute(
                EmployeesPersonalInformation.__table__.update()
                .where(EmployeesPersonalInformation.employee_id == cnp.cnp)
                .values({k: data[k] for k in {"position", "department"} & data.keys()})
            )

        if "email" in data:
            email_data = await session.execute(
                EmployeesEmail.__table__.select().where(EmployeesEmail.employee_id == cnp.cnp)
            )
            email = email_data.fetchone()
            if email:
                await session.execute(
                    EmployeesEmail.__table__.update()
                    .where(EmployeesEmail.employee_id == cnp.cnp)
                    .values(email=data["email"])
                )
            else:
                email_obj = EmployeesEmail(email=data["email"], employee_id=cnp.cnp)
                session.add(email_obj)

        await session.commit()
        return jsonify({"message": "Employee updated"})


@employee_bp.route("/employees/<int:id>", methods=["DELETE"])
async def delete_employee(id):
    async with async_session() as session:
        cnp_data = await session.execute(
            EmployeesCNP.__table__.select().where(EmployeesCNP.id == id)
        )
        cnp = cnp_data.fetchone()
        if not cnp:
            abort(404, "Employee not found")

        await session.execute(
            EmployeesName.__table__.delete().where(EmployeesName.employee_id == cnp.cnp)
        )
        await session.execute(
            EmployeesPersonalInformation.__table__.delete().where(EmployeesPersonalInformation.employee_id == cnp.cnp)
        )
        await session.execute(
            EmployeesEmail.__table__.delete().where(EmployeesEmail.employee_id == cnp.cnp)
        )
        await session.execute(
            EmployeesCNP.__table__.delete().where(EmployeesCNP.id == id)
        )

        await session.commit()
        return jsonify({"message": "Employee deleted"})
