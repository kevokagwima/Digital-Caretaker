from Models.base_model import db, BaseModel, UserBaseModel
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class Role(BaseModel, db.Model):
  __tablename__ = 'role'
  name = db.Column(db.String(20), nullable=False)
  users = db.relationship("Users", backref="users", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

  def __repr__(self):
    return f"{self.name}"

class Users(BaseModel, UserBaseModel, UserMixin, db.Model):
  __tablename__ = "users"
  role_id = db.Column(db.Integer(), db.ForeignKey("role.id"))
  property_owned = db.relationship("Property", backref="user_properties", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)
  subscription = db.relationship("Subscription", backref="user_subscription", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)
  payment = db.relationship("Payment", backref="user_payment", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)
  
  def __repr__(self):
    return f"{self.first_name} {self.last_name}"
