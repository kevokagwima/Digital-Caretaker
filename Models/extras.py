from Models.base_model import db, BaseModel, UserBaseModel
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class ExtraRoles(BaseModel, db.Model):
  __tablename__ = "extra_roles"
  name = db.Column(db.String(20), nullable=False)

class Extras(BaseModel, UserBaseModel, db.Model):
  __tablename__ = "extras"
  age = db.Column(db.Integer(), nullable=False)
  role = db.Column(db.String(15), nullable=False)
  rate = db.Column(db.Integer(), nullable=False)
  rating = db.Column(db.Integer(), nullable=False, default=0)
  extra_service = db.relationship("ExtraService", backref="extra services", lazy=True, cascade="all, delete, delete-orphan")

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

  def __repr__(self):
    return f"{self.first_name} {self.last_name} - {self.role}"

class ExtraService(BaseModel, db.Model):
  __tablename__ = 'extra_service'
  landlord = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  properties = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("unit.id"))
  extra = db.Column(db.Integer(), db.ForeignKey("extras.id"))
  rate = db.Column(db.Integer(), nullable=False, default=0)
  date_opened = db.Column(db.DateTime(), nullable=False)
  date_cancelled = db.Column(db.DateTime(), nullable=False)
  date_completed = db.Column(db.DateTime(), nullable=False)
  date_closed = db.Column(db.DateTime())
  is_active = db.Column(db.Boolean(), default=True)
  is_cancelled = db.Column(db.Boolean(), default=False)
  is_completed = db.Column(db.Boolean(), default=False)

  def __repr__(self):
    return f"{self.extra} - {self.cost}"
