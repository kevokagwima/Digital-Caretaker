from Models.base_model import db, BaseModel, UserBaseModel
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from Models.unit import Unit
from Models.transactions import Transactions
from Models.extras import ExtraService
from Models.complaints import Complaints
from Models.invoice import Invoice
from Models.property import Properties 

bcrypt = Bcrypt()

class Role(BaseModel, db.Model):
  __tablename__ = 'role'
  name = db.Column(db.String(20), nullable=False)
  admin = db.relationship("Admin", backref="admin", lazy=True, cascade="all, delete, delete-orphan")
  users = db.relationship("Users", backref="users", lazy=True, cascade="all, delete, delete-orphan")
  landlord = db.relationship("Landlord", backref="landlord", lazy=True, cascade="all, delete, delete-orphan")
  tenant = db.relationship("Tenant", backref="tenant_role", lazy=True, cascade="all, delete, delete-orphan")

  def __repr__(self):
    return f"{self.name}"

class Admin(BaseModel, UserBaseModel, UserMixin, db.Model):
  __tablename__ = 'admin'
  account_type = db.Column(db.Integer(), db.ForeignKey("role.id"))

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

class Users(BaseModel, UserBaseModel, UserMixin, db.Model):
  __tablename__ = "users"
  account_type = db.Column(db.Integer(), db.ForeignKey("role.id"))

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

class Landlord(BaseModel, UserBaseModel, UserMixin, db.Model):
  __tablename__ = "landlord"
  account_type = db.Column(db.Integer(), db.ForeignKey("role.id"))
  tenant = db.relationship("Tenant", backref="tenant", lazy=True, cascade="all, delete, delete-orphan")
  unit = db.relationship("Unit", backref="all_units", lazy=True, cascade="all, delete, delete-orphan")
  transaction = db.relationship("Transactions", backref="landlord_transaction", lazy=True, cascade="all, delete, delete-orphan")
  extra_service = db.relationship("ExtraService", backref="extra_service", lazy=True, cascade="all, delete, delete-orphan")
  properties = db.relationship("Properties", backref="property", lazy=True, cascade="all, delete, delete-orphan")
  complaint = db.relationship("Complaints", backref="complaint", lazy=True, cascade="all, delete, delete-orphan")

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

class Tenant(BaseModel, UserBaseModel, UserMixin, db.Model):
  __tablename__ = "tenant"
  account_type = db.Column(db.Integer(), db.ForeignKey("role.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  properties = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  is_active = db.Column(db.Boolean(), default=False)
  unit = db.relationship("Unit", backref="unit", lazy=True, cascade="all, delete, delete-orphan")
  complaint = db.relationship("Complaints", backref="complaints", lazy=True, cascade="all, delete, delete-orphan")
  transaction = db.relationship("Transactions", backref="tenant_transaction", lazy=True, cascade="all, delete, delete-orphan")
  invoice = db.relationship("Invoice", backref="tenant_invoice", lazy=True, cascade="all, delete, delete-orphan")

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)
