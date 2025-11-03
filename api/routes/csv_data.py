from flask import Blueprint, jsonify

from services.create_csv_file import generate_csv_data


csv_data_bp = Blueprint("csv_data", __name__)


@csv_data_bp.route("/createAggregatedEmployeeData/<int:id>", methods=["POST"])
async def create_csv_data(id):
    csv_path = await generate_csv_data(id)
    return jsonify({"CSV File Path": csv_path}), 201