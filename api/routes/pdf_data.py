from flask import Blueprint, jsonify

from services.create_pdf_file import generate_pdf_data


pdf_data_bp = Blueprint("pdf_data", __name__)


@pdf_data_bp.route("/createPdfForEmployees/<int:manager_id>/<int:employee_id>", methods=["POST"])
async def create_pdf_data(manager_id, employee_id):
    pdf_path = await generate_pdf_data(manager_id, employee_id)
    return jsonify({"PDF File Path": pdf_path}), 201
