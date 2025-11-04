from flask import Blueprint, jsonify

from services.create_csv_file import generate_csv_data
from services.send_email_file import send_email_message


csv_data_bp = Blueprint("csv_data", __name__)


@csv_data_bp.route("/createAggregatedEmployeeData/<int:id>", methods=["POST"])
async def create_csv_data(id):
    csv_path = await generate_csv_data(id)
    return jsonify({"CSV File Path": csv_path}), 201


@csv_data_bp.route("/sendAggregatedEmployeeData/<int:id>", methods=["POST"])
async def send_pdf_data(id):
    csv_path = await generate_csv_data(id)
    response = send_email_message(
        to_email="daniel-antoniu.dumitru@endava.com",
        subject="Employees data of the department",
        text="Good day! I attach the CSV with the details of each employee in the department.",
        file_path=csv_path,
        file_type="csv"
    )
    return jsonify({"PDF file path": csv_path}), response.status_code
