import bcrypt

from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_email_model import EmployeesEmail
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation

from api.schemas.employees_cnp_schema import EmployeesCNPSchema
from api.schemas.employees_email_schema import EmployeesEmailSchema
from api.schemas.employees_name_schema import EmployeesNameSchema
from api.schemas.employees_personal_information_schema import EmployeesPersonalInformationSchema

from db.session import async_session

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

auth_bp = Blueprint('auth', __name__)


async def validate_employee_request(data, required_fields = None):
    if required_fields is None:
        required_fields = {"cnp", "name", "surname", "password", "position", "department", "dateOfBirth", "dateOfHire", "email"}
    if set(data.keys()) != required_fields:
        abort(400, "Invalid employee request structure")
    return data


@auth_bp.route("/register", methods=["POST"])
async def register():
    data = validate_employee_request(request.get_json())
    async with async_session() as session:
        try:
            employee_check = await session.execute(
                select(EmployeesCNP).where(EmployeesCNP.cnp == data["cnp"])
            )

            employee_check_result = employee_check.scalar_one_or_none()
            if employee_check_result:
                abort(400, "Employee already registered")

            hashed_password = bcrypt.hashpw(
                data["password"].encode(), bcrypt.gensalt()
            ).decode()

            try:
                cnp_data = EmployeesCNPSchema.model_validate({
                    "cnp": data["cnp"]
                })
            except ValidationError:
                abort(422, "CNP validation failed")

            cnp = EmployeesCNP(**cnp_data.model_dump())
            session.add(cnp)

            try:
                name_data = EmployeesNameSchema.model_validate({
                    "name": data["name"],
                    "surname": data["surname"],
                    "password": hashed_password,
                    "employeeId": cnp.cnp
                })
            except ValidationError:
                abort(422, "Name validation failed")

            name = EmployeesName(**name_data.model_dump())
            session.add(name)

            try:
                email_data = EmployeesEmailSchema.model_validate({
                    "email": data["email"],
                    "employeeId": cnp.cnp
                })
            except ValidationError:
                abort(422, "Email validation failed")

            email = EmployeesEmail(**email_data.model_dump())
            session.add(email)

            try:
                personal_data = EmployeesPersonalInformationSchema.model_validate({
                    "position": data["position"],
                    "department": data["department"],
                    "dateOfBirth": data["dateOfBirth"],
                    "dateOfHire": data["dateOfHire"],
                    "employeeId": cnp.cnp
                })
            except ValidationError:
                abort(422, "Personal information validation failed")

            personal = EmployeesPersonalInformation(**personal_data.model_dump())
            session.add(personal)

            await session.commit()

            access_token = create_access_token(identity={
                "email": data["email"],
                "position": data["position"],
                "department": data["department"]
            })

            refresh_token = create_refresh_token(identity={
                "email": data["email"],
                "position": data["position"],
                "department": data["department"]
            })

            return jsonify(
                message="Employee registered successfully",
                access_token=access_token,
                refresh_token=refresh_token
            ), 201
        except MultipleResultsFound:
            abort(500, "Multiple entries found for the user")
        except SQLAlchemyError:
            abort(500, "Database error")
        except Exception:
            abort(500, "Unknown error")


@auth_bp.route("/login", methods=["POST"])
async def login():
    data = validate_employee_request(request.get_json(), required_fields={"email", "password"})
    async with async_session() as session:
        try:
            email_data = await session.execute(
                select(EmployeesEmail).where(EmployeesEmail.email == data["email"])
            )

            email = email_data.scalar_one_or_none()
            if not email:
                abort(404, "Email not found")

            employee_id = email.employee_id

            name_data = await session.execute(
                select(EmployeesName).where(EmployeesName.employee_id == employee_id)
            )

            name = name_data.scalar_one_or_none()
            if not name:
                abort(404, "Employee name not found")

            registration_password = name.password.encode()
            login_password = data["password"].encode()
            if not bcrypt.checkpw(login_password, registration_password):
                abort(401, "Invalid password")

            personal_information_data = await session.execute(
                select(EmployeesPersonalInformation)
                .where(EmployeesPersonalInformation.employee_id == employee_id)
            )

            personal_information = personal_information_data.scalar_one_or_none()
            if not personal_information:
                abort(404, "Employee personal information not found")

            access_token = create_access_token(identity={
                "email": data["email"],
                "position": personal_information.position,
                "department": personal_information.department
            })

            refresh_token = create_refresh_token(identity={
                "email": data["email"],
                "position": personal_information.position,
                "department": personal_information.department
            })

            return jsonify(
                message="Employee logged successfully",
                access_token=access_token,
                refresh_token=refresh_token
            ), 200
        except MultipleResultsFound:
            abort(500, "Multiple entries found for the email")
        except SQLAlchemyError:
            abort(500, "Database error")
        except Exception:
            abort(500, "Unknown error")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
async def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify(
        message="Access token refreshed successfully",
        access_token=access_token
    ), 200
