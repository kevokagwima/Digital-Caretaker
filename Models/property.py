from Models.base_model import db, BaseModel
from Models.unit import Unit
from Models.bookings import Bookings
from Models.extras import ExtraService
from Models.transactions import Transactions
from Models.complaints import Complaints
from datetime import datetime

class PropertyTypes(BaseModel, db.Model):
  __tablename__ = 'property_types'
  name = db.Column(db.String(30), nullable=False)
  properties = db.relationship("Properties", backref="properties", lazy=True, cascade="all, delete, delete-orphan")

  def __repr__(self):
    return f"{self.name}"

class UnitTypes(BaseModel, db.Model):
  __tablename__ = 'unit_types'
  name = db.Column(db.String(30), nullable=False)
  properties = db.Column(db.Integer(), db.ForeignKey("properties.id"))

  def __repr__(self):
    return f"{self.name}"

class Properties(BaseModel, db.Model):
  __tablename__ = "properties"
  name = db.Column(db.String(50), nullable=False)
  county = db.Column(db.String(50), nullable=False)
  city = db.Column(db.String(50), nullable=False)
  property_floors = db.Column(db.Integer(), nullable=False)
  rooms = db.Column(db.Integer(), nullable=False)
  date_added = db.Column(db.DateTime())
  property_type = db.Column(db.Integer(), db.ForeignKey("property_types.id"))
  property_owner = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  unit = db.relationship("Unit", backref="units", lazy=True, cascade="all, delete, delete-orphan")
  tenant = db.relationship("Tenant", backref="tenants", lazy=True, cascade="all, delete, delete-orphan")
  booking = db.relationship("Bookings", backref="property_booked", lazy=True, cascade="all, delete, delete-orphan")
  complaint = db.relationship("Complaints", backref="complaintz", lazy=True, cascade="all, delete, delete-orphan")
  transaction = db.relationship("Transactions", backref="property_transaction", lazy=True, cascade="all, delete, delete-orphan")
  extra_service = db.relationship("ExtraService", backref="extras", lazy=True, cascade="all, delete, delete-orphan")
  unit_type = db.relationship("UnitTypes", backref="unit_types", lazy=True, cascade="all, delete, delete-orphan")

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.date_added = datetime.now()
  
  def __repr__(self):
    return f"{self.name}"
