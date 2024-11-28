from functools import wraps
from flask import abort, request
from flask_login import current_user

def landlord_role_required(role_name):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if current_user.is_authenticated and current_user.landlord.name == role_name:
        return f(*args, **kwargs)
      else:
        abort(403)
    return decorated_function
  return decorator

def tenant_role_required(role_name):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if current_user.is_authenticated and current_user.tenant_role.name == role_name:
        return f(*args, **kwargs)
      else:
        abort(403)
    return decorated_function
  return decorator

def admin_role_required(role_name):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if current_user.is_authenticated and current_user.admin.name == role_name:
        return f(*args, **kwargs)
      else:
        abort(403)
    return decorated_function
  return decorator
