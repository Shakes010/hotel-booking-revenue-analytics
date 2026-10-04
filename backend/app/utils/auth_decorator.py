from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def role_required(allowed_roles):
    """
    Custom decorator to restrict API access based on user role names.
    Usage: @role_required(['Admin', 'Hotel Manager'])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Unauthorized: Token missing or invalid'}), 401
            
            user = User.query.get(current_user_id)
            if not user or not user.role:
                return jsonify({'error': 'Forbidden: User identity invalid'}), 403

            if user.role.role_name not in allowed_roles:
                return jsonify({'error': f'Forbidden: Requires one of {allowed_roles} roles'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
