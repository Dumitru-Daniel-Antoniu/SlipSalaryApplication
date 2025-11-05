import os

from flask import Blueprint, jsonify

from services.archive_files import archive_file
from services.create_pdf_file import generate_pdf_data
from services.send_email_file import send_email_message


pdf_data_bp = Blueprint("pdf_data", __name__)


@pdf_data_bp.route("/createPdfForEmployees/<int:manager_id>/<int:employee_id>", methods=["POST"])
async def create_pdf_data(manager_id, employee_id):
    pdf_path = await generate_pdf_data(manager_id, employee_id)
    return jsonify({"PDF File Path": pdf_path}), 201


@pdf_data_bp.route("/sendPdfToEmployees/<int:manager_id>/<int:employee_id>", methods=["POST"])
async def send_pdf_data(manager_id, employee_id):
    pdf_path = await generate_pdf_data(manager_id, employee_id)
    archive_path = await archive_file(
        pdf_path,
        "pdf",
        "ddumitru128@gmail.com",
        "ddumitru128@gmail.com",
        os.path.basename(pdf_path)
    )
    response = await send_email_message(
        to_email="ddumitru128@gmail.com",
        subject="Employee salary",
        text="Good day! I attach the PDF with the salary details of the current month.",
        file_path=pdf_path,
        file_type="pdf"
    )

    if response.status_code != 200:
        if os.path.exists(archive_path):
            os.remove(archive_path)

    return jsonify({"PDF file path": pdf_path, "PDF archive path": archive_path}), response.status_code
