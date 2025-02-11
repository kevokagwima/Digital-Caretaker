from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)

@errors.app_errorhandler(401)
def error_401(error):
  message = "Error. Unauthorized request"
  return render_template("Errors/401.html", error=error, message=message), 401

@errors.app_errorhandler(403)
def error_403(error):
  message = "You're not authorized to access this page"
  return render_template("Errors/403.html", message=message, error=error), 403

@errors.app_errorhandler(404)
def error_404(error):
  message = "Error. Page Not Found"
  return render_template("Errors/404.html", message=message, error=error), 404

@errors.app_errorhandler(405)
def error_405(error):
  message = "Error. Method not allowed"
  return render_template("Errors/405.html", error=error, message=message), 405

@errors.app_errorhandler(500)
def error_500(error):
  message = "Error. Server is down"
  return render_template("Errors/500.html", error=error, message=message), 500
