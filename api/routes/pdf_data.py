import logging
import os

from api.decorators.manager_required import manager_required
from api.schemas.idempotency_schema import IdempotencyKeySchema

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from services.archive_files import archive_file
from services.create_pdf_file import generate_pdf_data
from services.idempotency_service import get_idempotent_response, store_idempotent_response
from services.send_email_file import send_email_message


logging.basicConfig(level=logging.INFO)

host_email = os.getenv("EMAIL_ADDRESS")

pdf_data_bp = Blueprint("pdf_data", __name__)


@pdf_data_bp.route("/createPdfForEmployees/<int:manager_id>/<int:employee_id>", methods=["POST"])
# @manager_required
async def create_pdf_data(manager_id, employee_id):
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

    pdf_path = await generate_pdf_data(manager_id, employee_id)

    response = {"PDF File Path": pdf_path}
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


@pdf_data_bp.route("/sendPdfToEmployees/<int:manager_id>/<int:employee_id>", methods=["POST"])
# @manager_required
async def send_pdf_data(manager_id, employee_id):
    idempotency_key = request.headers.get("Idempotency-Key")
    email = request.headers.get("Email")
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

    pdf_path = await generate_pdf_data(manager_id, employee_id)
    archive_path = await archive_file(
        pdf_path,
        "pdf",
        host_email,
        email,
        os.path.basename(pdf_path)
    )
    response = await send_email_message(
        to_email=email,
        subject="Employee salary",
        text="Good day! I attach the PDF with the salary details of the current month. To unlock it, use your CNP. Have a great day!",
        file_path=pdf_path,
        file_type="pdf"
    )

    logging.info("Email send response status code: %d", response)

    if response != 200:
        if os.path.exists(archive_path):
            os.remove(archive_path)

    logging.info("Response status code: %d", response)

    response_paths = {"PDF file path": pdf_path, "PDF archive path": archive_path}

    key = IdempotencyKeySchema.model_validate({
        "key": idempotency_key,
        "endpoint": endpoint,
        "response_data": response_paths,
        "status_code": response,
        "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
    })

    await store_idempotent_response(key)

    return jsonify(response_paths), response