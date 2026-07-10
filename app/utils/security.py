from functools import wraps
from flask import abort, g, redirect, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required(optional=True)
        def wrapper(*args, **kwargs):
            current_identity = get_jwt_identity()
            print("JWT Identity:", current_identity)
            if not current_identity:
                return redirect(url_for("auth.login"))
            from app.models import User
            user = User.query.get(int(current_identity))
            if not user or not user.is_active:
                return redirect(url_for("auth.login"))
            if user.role.name not in roles:
                abort(403)
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator
