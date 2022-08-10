from os import abort
from flask import Flask
from models import db, Landlord, Tenant, Members
from flask_login import login_manager, LoginManager
from flask_session import Session
from config import Config
from Landlords.routes import landlords
from Tenants.routes import tenants
from Main.routes import main
from Admin.routes import admins
from Errors.handlers import errors

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(landlords)
app.register_blueprint(tenants)
app.register_blueprint(main)
app.register_blueprint(admins)
app.register_blueprint(errors)

db.init_app(app)
Session(app)
login_manager = LoginManager()
login_manager.blueprint_login_views = {
  'landlord' : '/landlord_login',
  'tenant' : '/tenant_authentication',
  'main' : '/signin'
}
login_manager.login_message_category = "danger"
login_manager.refresh_view = 'main.signin'
login_manager.needs_refresh_message = "Your previous session timed out. Login again"
login_manager.needs_refresh_message_category = "info"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Landlord.query.filter_by(phone=user_id).first() or Tenant.query.filter_by(phone=user_id).first() or Members.query.filter_by(phone=user_id).first()
  except:
    abort(500)

if __name__ == "__main__":
  app.run(debug=True, port=5001)
