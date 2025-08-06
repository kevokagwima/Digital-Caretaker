from Models.base_model import db, BaseModel
from Models.bookings import Bookings
from Models.transactions import Transactions
from Models.invoice import Invoice
from Models.extras import Maintenance

class UnitTypes(BaseModel, db.Model):
  __tablename__ = 'unit_types'
  name = db.Column(db.String(30), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))

  def __repr__(self):
    return f"{self.name}"

class Unit(BaseModel, db.Model):
  __tablename__ = "unit"
  name = db.Column(db.String(100), nullable=False)
  alias = db.Column(db.String(100), nullable=False, default=name)
  description = db.Column(db.Text())
  unit_floor = db.Column(db.Integer(), nullable=False)
  unit_type = db.Column(db.String(50), nullable=False)
  rent_amount = db.Column(db.Integer(), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  tenant_id = db.Column(db.Integer(), db.ForeignKey("tenant.id"))
  landlord_id = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  is_reserved = db.Column(db.Boolean(), default=False)
  booking = db.relationship("Bookings", backref="unit_booked", lazy=True, cascade="all, delete, delete-orphan")
  transaction = db.relationship("Transactions", backref="unit_transaction", lazy=True, cascade="all, delete, delete-orphan")
  invoice = db.relationship("Invoice", backref="unit_invoice", lazy=True, cascade="all, delete, delete-orphan")
  maintenace = db.relationship("Maintenance", backref="unit_maintenance", lazy=True, cascade="all, delete, delete-orphan")
  unit_image = db.relationship("UnitImage", backref="image", lazy=True, cascade="all, delete, delete-orphan")
  unit_metrics = db.relationship("UnitMetrics", backref="metrics", lazy=True, cascade="all, delete, delete-orphan")

  def __repr__(self):
    return f"{self.name} - {self.unit_floor}"

class UnitMetrics(BaseModel, db.Model):
  __tablename__  = "unit_metrics"
  living_space = db.Column(db.Integer(), nullable=False, default=0)
  balcony_space = db.Column(db.Integer(), nullable=False, default=0)
  bedrooms = db.Column(db.Integer(), nullable=False, default=0)
  bathrooms = db.Column(db.Integer(), nullable=False, default=0)
  unit_id = db.Column(db.Integer(), db.ForeignKey("unit.id"))

  def __repr__(self):
    return f"{self.living_space}, {self.balcony_space}, {self.bedrooms}, {self.bathrooms}"

class UnitImage(BaseModel, db.Model):
  __tablename__ = "unit_image"
  name = db.Column(db.String(200), nullable=False)
  bucket = db.Column(db.String(50), nullable=False)
  region = db.Column(db.String(20), nullable=False)
  unit = db.Column(db.Integer(), db.ForeignKey("unit.id"))

  def __repr__(self):
    return f"{self.name}"
