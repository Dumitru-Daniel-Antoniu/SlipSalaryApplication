import os

from api.decorators.manager_required import manager_required
from api.schemas.idempotency_schema import IdempotencyKeySchema

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from services.archive_files import archive_file
from services.create_csv_file import generate_csv_data
from services.idempotency_service import get_idempotent_response, store_idempotent_response
from services.send_email_file import send_email_message


csv_data_bp = Blueprint("csv_data", __name__)


@csv_data_bp.route("/createAggregatedEmployeeData/<int:employee_id>", methods=["POST"])
@manager_required
async def create_csv_data(employee_id):
    idempotency_key = request.headers.get("Idempotency-Key")
    endpoint = request.path

    if not idempotency_key:
        return jsonify({"error": "Missing Idempotency-Key header"}), 400

    try:
        response_data, status_code = await get_idempotent_response(idempotency_key, endpoint)
        return jsonify(response_data), status_code
    except Exception as e:
        if getattr(e, "code", None) == 404:
            pass
        else:
            raise

    csv_path = await generate_csv_data(employee_id)

    response = {"PDF File Path": csv_path}
    status_code = 201

    key = IdempotencyKeySchema.model_validate({
        "key": idempotency_key,
        "endpoint": endpoint,
        "response_data": response,
        "status_code": status_code,
        "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
    })

    await store_idempotent_response(key)

    return jsonify(response), status_code


@csv_data_bp.route("/sendAggregatedEmployeeData/<int:employee_id>", methods=["POST"])
@manager_required
async def send_pdf_data(employee_id):
    idempotency_key = request.headers.get("Idempotency-Key")
    endpoint = request.path

    if not idempotency_key:
        return jsonify({"error": "Missing Idempotency-Key header"}), 400

    try:
        response_data, status_code = await get_idempotent_response(idempotency_key, endpoint)
        return jsonify(response_data), status_code
    except Exception as e:
        if getattr(e, "code", None) == 404:
            pass
        else:
            raise

    csv_path = await generate_csv_data(employee_id)
    archive_path = await archive_file(
        csv_path,
        "csv",
        "ddumitru128@gmail.com",
        "ddumitru128@gmail.com",
        os.path.basename(csv_path)
    )
    response = await send_email_message(
        to_email="ddumitru128@gmail.com",
        subject="Employees data of the department",
        text="Good day! I attach the CSV with the details of each employee in the department.",
        file_path=csv_path,
        file_type="csv"
    )

    if response.status_code != 200:
        if os.path.exists(archive_path):
            os.remove(archive_path)

    response_paths = {"PDF file path": csv_path, "PDF archive path": archive_path}

    key = IdempotencyKeySchema.model_validate({
        "key": idempotency_key,
        "endpoint": endpoint,
        "response_data": response_paths,
        "status_code": response.status_code,
        "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
    })

    await store_idempotent_response(key)

    return jsonify(response_paths), response.status_code
