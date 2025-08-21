from flask import Flask, flash
from flask_login import LoginManager
from Models.base_model import db
from Models.users import Users
from flask_migrate import Migrate
from config import Config
from Auth.routes import auth
from Dalali.routes import dalali, cache
from Client.routes import client
from Main.routes import main
from Admin.routes import admin
from Payments.routes import payments
from Errors.handlers import errors

def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)
  db.init_app(app)
  Migrate(app, db)
  login_manager = LoginManager()
  login_manager.init_app(app)
  cache.init_app(app)

  app.register_blueprint(auth)
  app.register_blueprint(dalali)
  app.register_blueprint(client)
  app.register_blueprint(main)
  app.register_blueprint(payments)
  app.register_blueprint(admin)
  app.register_blueprint(errors)

  login_manager.blueprint_login_views = {
    'dalali': '/auth/signin',
    'client': '/auth/signin',
    'admin': '/auth/signin',
  }
  login_manager.login_message_category = "danger"
  login_manager.refresh_view = '/auth/signin'
  login_manager.needs_refresh_message = "Your previous session timed out. Login again"
  login_manager.needs_refresh_message_category = "info"

  @login_manager.user_loader
  def load_user(user_id):
    try:
      return Users.query.filter_by(unique_id=user_id).first()
    except Exception as e:
      flash(f"Error loading user: {str(e)}", "danger")

  return app

if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)
