from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user_role = identity.get("role")
            if user_role not in roles:
                return jsonify({"msg": "Access denied: role not authorized"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
