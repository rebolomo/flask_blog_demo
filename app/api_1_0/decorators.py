from functools import wraps
from flask import g
from .errors import bad_request


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return bad_request(PERMISSION_LIMITED)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
