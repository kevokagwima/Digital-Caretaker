from flask import Flask, abort
from models import db, Landlord, Tenant, Users, Admin, Unit
from flask_login import login_manager, LoginManager, current_user, login_required
from flask_migrate import Migrate
from config import Config
from Auth.routes import auth
from Landlords.routes import landlords
from Tenants.routes import tenants
from Main.routes import main
from Admin.routes import admins
from Errors.handlers import errors
from modules import generate_invoice

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(auth)
app.register_blueprint(landlords)
app.register_blueprint(tenants)
app.register_blueprint(main)
app.register_blueprint(admins)
app.register_blueprint(errors)

db.init_app(app)
Migrate(app, db)
login_manager = LoginManager()
login_manager.blueprint_login_views = {
  'landlord': '/auth/landlord-login',
  'tenant': '/auth/tenant-login',
  'main': '/auth/signin',
  'admin': '/auth/admin-login'
}
login_manager.login_message_category = "danger"
login_manager.refresh_view = 'auth.signin'
login_manager.needs_refresh_message = "Your previous session timed out. Login again"
login_manager.needs_refresh_message_category = "info"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Landlord.query.filter_by(unique_id=user_id).first() or Tenant.query.filter_by(unique_id=user_id).first() or Users.query.filter_by(unique_id=user_id).first() or Admin.query.filter_by(unique_id=user_id).first()
  except:
    abort(500)

@app.before_request
def invoice():
  units = Unit.query.filter(Unit.tenant != None).all()
  if units:
    for unit in units:
      generate_invoice(unit.id, unit.tenant, unit.rent_amount)

if __name__ == "__main__":
  app.run(debug=True)
