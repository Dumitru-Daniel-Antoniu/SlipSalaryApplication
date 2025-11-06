from flask import Blueprint, jsonify, abort
from db.session import async_session
from db.models.idempotency_model import IdempotencyKey
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)

idempotency_bp = Blueprint("idempotency", __name__)


@idempotency_bp.route("/idempotency/clear", methods=["DELETE"])
async def clear_idempotency():
    """
    Delete all rows from the idempotency_keys table.
    """
    async with async_session() as session:
        try:
            await session.execute(IdempotencyKey.__table__.delete())
            await session.commit()
            return jsonify({"message": "All idempotency keys deleted"}), 200
        except SQLAlchemyError:
            logging.exception("Database error while clearing idempotency keys")
            abort(500, "Database error")
        except Exception:
            logging.exception("Unknown error while clearing idempotency keys")
            abort(500, "Unknown error")
