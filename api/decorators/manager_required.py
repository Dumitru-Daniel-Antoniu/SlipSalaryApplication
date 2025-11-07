from flask import abort
from flask_jwt_extended import get_jwt_identity, jwt_required

from functools import wraps


def manager_required(fn):
    @jwt_required()
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get("sub").get("position").lower().strip() != "manager":
            abort(403, "Manager position required")
        return await fn(*args, **kwargs)
    return wrapper
