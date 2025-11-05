import logging

from api.schemas.idempotency_schema import IdempotencyKeySchema

from db.models.idempotency_model import IdempotencyKey
from db.session import async_session

from flask import abort

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

logging.basicConfig(level=logging.INFO)


async def get_idempotent_response(key: str, endpoint: str):
    async with async_session() as session:
        try:
            statement = select(IdempotencyKey).where(
                IdempotencyKey.key == key,
                IdempotencyKey.endpoint == endpoint
            )

            logging.info("Result time")
            result = await session.execute(statement)
            logging.info("Result obtained %s", result)

            entry = result.scalar_one_or_none()
            logging.info("Entry found: %s", entry)
        except MultipleResultsFound:
            abort(500, "Multiple entries found for the given idempotency key and endpoint")
        except SQLAlchemyError:
            logging.info("Database error occurred at get_idempotent_response")
            abort(500, "Database error")
        except Exception:
            abort(500, "Unknown error")

        if entry is None:
            logging.info("Entry not found")
            abort(404, "Idempotency key not found")

        return entry.response_data, entry.status_code


async def store_idempotent_response(idempotency_data: IdempotencyKeySchema):
    async with async_session() as session:
        try:
            logging.info("Entry creation")
            entry = IdempotencyKey(**idempotency_data.model_dump())
            logging.info("Create the entry")

            session.add(entry)
            logging.info("Entry addeed")
            try:
                await session.commit()
            except Exception as e:
                logging.error("Commit failed: %s", e)
                raise
            logging.info("Entry committed")

            return entry
        except SQLAlchemyError:
            logging.info("Database error occurred at store_idempotent_response")
            abort(500, "Database error")
        except Exception:
            abort(500, "Unknown error")
