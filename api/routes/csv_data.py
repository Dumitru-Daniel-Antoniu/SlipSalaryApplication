import os

from flask import Blueprint, jsonify

from services.archive_files import archive_file
from services.create_csv_file import generate_csv_data
from services.send_email_file import send_email_message


csv_data_bp = Blueprint("csv_data", __name__)


@csv_data_bp.route("/createAggregatedEmployeeData/<int:employee_id>", methods=["POST"])
async def create_csv_data(employee_id):
    csv_path = await generate_csv_data(employee_id)
    return jsonify({"CSV File Path": csv_path}), 201


@csv_data_bp.route("/sendAggregatedEmployeeData/<int:employee_id>", methods=["POST"])
async def send_pdf_data(employee_id):
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

    return jsonify({"CSV file path": csv_path, "CSV archive path": archive_path}), response.status_code
