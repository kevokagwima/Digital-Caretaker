from flask import Flask, abort, session, request, redirect, url_for
from flask_login import LoginManager
from Models.base_model import db
from Models.users import Admin, Landlord, Tenant, Users
from Models.unit import Unit
from flask_migrate import Migrate
from flask_babel import Babel, _, lazy_gettext
from config import Config
from Auth.routes import auth
from Landlords.routes import landlords
from Tenants.routes import tenants
from Main.routes import main
from Admin.routes import admins
from Payments.routes import payments
from Errors.handlers import errors
from modules import generate_invoice

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  Migrate(app, db)
  login_manager = LoginManager()
  login_manager.init_app(app)
  babel = Babel(app)

  app.register_blueprint(auth)
  app.register_blueprint(landlords)
  app.register_blueprint(tenants)
  app.register_blueprint(main)
  app.register_blueprint(payments)
  app.register_blueprint(admins)
  app.register_blueprint(errors)

  login_manager.blueprint_login_views = {
    'landlord': '/auth/landlord/login',
    'tenant': '/auth/tenant/login',
    'admin': '/auth/admin/login',
    'main': '/auth/signin'
  }
  login_manager.login_message_category = "danger"
  login_manager.refresh_view = 'auth.signin'
  login_manager.needs_refresh_message = "Your previous session timed out. Login again"
  login_manager.needs_refresh_message_category = "info"

  @login_manager.user_loader
  def load_user(user_id):
    try:
      return Landlord.query.filter_by(unique_id=user_id).first() or Tenant.query.filter_by(unique_id=user_id).first() or Users.query.filter_by(unique_id=user_id).first() or Admin.query.filter_by(unique_id=user_id).first()
    except Exception as e:
      print(f"Error loading user: {repr(e)}", category="danger")
      abort(500)

  @app.before_request
  def set_locale():
    # 1. Check if language is set in session
    if 'language' in session:
      babel.locale = session['language']
    # 2. Fall back to browser preference
    else:
      babel.locale = request.accept_languages.best_match(['en', 'sw'])
    
  @app.route('/set_lang/<lang>')
  def set_lang(lang):
    if lang in Config.LANGUAGES:
      session['language'] = lang
      babel.locale = lang
    return redirect(request.referrer or url_for('index'))

  @app.before_request
  def invoice():
    units = Unit.query.filter(Unit.tenant != None).all()
    if units:
      for unit in units:
        generate_invoice(unit.id, unit.tenant, unit.rent_amount)
  return app

if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)
