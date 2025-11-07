import bcrypt
import logging

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
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError


logging.basicConfig(level=logging.INFO)

auth_bp = Blueprint('auth', __name__)

token_blocklist = set()


def validate_employee_request(data, required_fields = None):
    if required_fields is None:
        required_fields = {"cnp", "name", "surname", "password", "position", "department", "dateOfBirth", "dateOfHire", "email"}
    logging.info("Validating employee request data: %s", data)
    if not isinstance(data, dict):
        logging.error("Invalid JSON body")
        abort(400, "Invalid JSON body")
    if set(data.keys()) != required_fields:
        logging.error("Invalid employee request structure")
        abort(400, "Invalid employee request structure")
    return data


@auth_bp.route("/register", methods=["POST"])
async def register():
    data = validate_employee_request(request.get_json())
    async with async_session() as session:
        try:
            logging.info("Attempting to register employee with CNP: %s", data["cnp"])
            employee_check = await session.execute(
                select(EmployeesCNP).where(EmployeesCNP.cnp == data["cnp"])
            )

            logging.info("Employee check query result: %s", employee_check)
            employee_check_result = employee_check.scalar_one_or_none()
            if employee_check_result:
                logging.error("Employee already registered with CNP: %s", data["cnp"])
                abort(400, "Employee already registered")

            logging.info("Hashing password for employee with CNP: %s", data["cnp"]) 
            hashed_password = bcrypt.hashpw(
                data["password"].encode(), bcrypt.gensalt()
            ).decode()

            try:
                logging.info("Validating CNP data for employee with CNP: %s", data["cnp"])
                cnp_data = EmployeesCNPSchema.model_validate({
                    "cnp": data["cnp"]
                })
            except ValidationError:
                logging.error("CNP validation failed for CNP: %s", data["cnp"])
                abort(422, "CNP validation failed")

            cnp = EmployeesCNP(**cnp_data.model_dump())
            session.add(cnp)

            logging.info("Validating name data for employee with CNP: %s", data["cnp"])
            try:
                logging.info("Creating name data for employee with CNP: %s", data["cnp"])
                logging.info(type(data["name"]))
                logging.info(type(data["surname"]))
                logging.info(type(hashed_password))
                logging.info(type(cnp.cnp)) 
                name_data = EmployeesNameSchema.model_validate({
                    "name": data["name"],
                    "surname": data["surname"],
                    "password": hashed_password,
                    "employeeId": cnp.cnp
                })
            except ValidationError as e:
                logging.error("Name validation failed for employee with CNP: %s", data["cnp"])
                logging.error("Validation error message: %s", str(e))
                logging.error("Validation error details: %s", e.errors())
                abort(422, "Name validation failed")

            name = EmployeesName(**name_data.model_dump())
            session.add(name)

            logging.info("Validating email data for employee with CNP: %s", data["cnp"])
            try:
                logging.info("Creating email data for employee with CNP: %s", data["cnp"])
                email_data = EmployeesEmailSchema.model_validate({
                    "email": data["email"],
                    "employeeId": cnp.cnp
                })
            except ValidationError:
                logging.error("Email validation failed for employee with CNP: %s", data["cnp"])
                abort(422, "Email validation failed")

            email = EmployeesEmail(**email_data.model_dump())
            session.add(email)

            logging.info("Validating personal information data for employee with CNP: %s", data["cnp"])
            try:
                logging.info("Creating personal information data for employee with CNP: %s", data["cnp"])
                personal_data = EmployeesPersonalInformationSchema.model_validate({
                    "position": data["position"],
                    "department": data["department"],
                    "dateOfBirth": data["dateOfBirth"],
                    "dateOfHire": data["dateOfHire"],
                    "employeeId": cnp.cnp
                })
            except ValidationError:
                logging.error("Personal information validation failed for employee with CNP: %s", data["cnp"])
                abort(422, "Personal information validation failed")

            personal = EmployeesPersonalInformation(**personal_data.model_dump())
            session.add(personal)

            logging.info("Committing new employee with CNP: %s to the database", data["cnp"])
            await session.commit()

            logging.info("Creating tokens for employee with CNP: %s", data["cnp"])
            access_token = create_access_token(identity={
                "name": data["name"],
                "surname": data["surname"],
                "email": data["email"],
                "position": data["position"],
                "department": data["department"]
            })

            logging.info("Access token created: %s", access_token)
            refresh_token = create_refresh_token(identity={
                "name": data["name"],
                "surname": data["surname"],
                "email": data["email"],
                "position": data["position"],
                "department": data["department"]
            })

            logging.info("Refresh token created: %s", refresh_token)
            return jsonify(
                message="Employee registered successfully",
                access_token=access_token,
                refresh_token=refresh_token
            ), 201
        except MultipleResultsFound:
            logging.error("Multiple entries found for the user with CNP: %s", data["cnp"])
            abort(500, "Multiple entries found for the user")
        except SQLAlchemyError:
            logging.error("Database error occurred")
            abort(500, "Database error")
        except Exception:
            logging.error("Unknown error occurred")
            abort(500, "Unknown error")


@auth_bp.route("/login", methods=["POST"])
async def login():
    data = validate_employee_request(request.get_json(), required_fields={"email", "password"})
    async with async_session() as session:
        try:
            logging.info("Attempting to log in with email: %s", data["email"])
            email_data = await session.execute(
                select(EmployeesEmail).where(EmployeesEmail.email == data["email"])
            )

            logging.info("Searching for email: %s", email_data)
            email = email_data.scalar_one_or_none()
            if not email:
                logging.error("Email not found: %s", data["email"])
                abort(404, "Email not found")

            logging.info("Email found: %s", email.email)
            employee_id = email.employee_id
            logging.info("Corresponding employee ID: %s", employee_id)

            name_data = await session.execute(
                select(EmployeesName).where(EmployeesName.employee_id == employee_id)
            )

            logging.info("Name data query result: %s", name_data)
            name = name_data.scalar_one_or_none()
            if not name:
                logging.error("Employee name not found: %s", name)
                abort(404, "Employee name not found")


            registration_password = name.password.encode()
            login_password = data["password"].encode()
            if not bcrypt.checkpw(login_password, registration_password):
                logging.error("Invalid password")
                abort(401, "Invalid password")

            personal_information_data = await session.execute(
                select(EmployeesPersonalInformation)
                .where(EmployeesPersonalInformation.employee_id == employee_id)
            )

            personal_information = personal_information_data.scalar_one_or_none()
            if not personal_information:
                logging.error("Employee personal information not found: %s", personal_information)
                abort(404, "Employee personal information not found")

            access_token = create_access_token(identity={
                "name": name.name,
                "surname": name.surname,
                "email": data["email"],
                "position": personal_information.position,
                "department": personal_information.department
            })

            logging.info("Access token created: %s", access_token)
            refresh_token = create_refresh_token(identity={
                "name": name.name,
                "surname": name.surname,
                "email": data["email"],
                "position": personal_information.position,
                "department": personal_information.department
            })

            logging.info("Refresh token created: %s", refresh_token)
            return jsonify(
                message="Employee logged successfully",
                access_token=access_token,
                refresh_token=refresh_token
            ), 200
        except MultipleResultsFound:
            logging.error("Multiple entries found for the email: %s", data["email"])
            abort(500, "Multiple entries found for the email")
        except SQLAlchemyError:
            logging.error("Database error occurred")
            abort(500, "Database error")
        except Exception as e:
            logging.error("An unknown error occurred %s", str(e))
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


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
async def logout():
    try:
        jwt_payload = get_jwt()
        jti = jwt_payload.get("jti")
        if jti:
            token_blocklist.add(jti)
            logging.info("Token revoked (jti=%s)", jti)
        return jsonify(message="Logged out successfully"), 200
    except Exception as e:
        logging.exception("Error during logout: %s", str(e))
        abort(500, "Logout failed")
