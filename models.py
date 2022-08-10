from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

class Members(db.Model, UserMixin):
  __tablename__ = "members"
  id = db.Column(db.Integer(), primary_key=True)
  first_name = db.Column(db.String(length=50), nullable=False)
  second_name = db.Column(db.String(length=50), nullable=False)
  last_name = db.Column(db.String(length=50), nullable=False)
  email = db.Column(db.String(length=100), nullable=False, unique=True)
  phone = db.Column(db.Integer(), nullable=False, unique=True)
  date = db.Column(db.DateTime())
  username = db.Column(db.String(length=50), nullable=False, unique=True)
  password = db.Column(db.String, nullable=False)
  bookings = db.relationship("Bookings", backref="booking", lazy=True)
  account_type = db.Column(db.String(length=10), nullable=False)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Landlord(db.Model, UserMixin):
  __tablename__ = "Landlord"
  id = db.Column(db.Integer(), primary_key=True)
  first_name = db.Column(db.String(length=50), nullable=False)
  second_name = db.Column(db.String(length=50), nullable=False)
  last_name = db.Column(db.String(length=50), nullable=False)
  email = db.Column(db.String(length=100), nullable=False, unique=True)
  phone = db.Column(db.Integer(), nullable=False, unique=True)
  username = db.Column(db.String(length=50), nullable=False, unique=True)
  date = db.Column(db.DateTime())
  landlord_id = db.Column(db.Integer(), nullable=False, unique=True)
  account_type = db.Column(db.String(length=10), nullable=False)
  password = db.Column(db.String(), nullable=False)
  tenant = db.relationship("Tenant", backref="tenant", lazy=True)
  complaint = db.relationship("Complaints", backref="complaint", lazy=True)
  unit = db.relationship("Unit", backref="all_units", lazy=True)
  Property = db.relationship("Properties", backref="property", lazy=True)
  active = db.Column(db.String(length=5), nullable=False)
  bookings = db.relationship("Bookings", backref="landlord_booking", lazy=True)
  transact = db.relationship("Transaction", backref="landlord_transaction", lazy=True)
  verification = db.relationship("Verification", backref="landlord-verification", lazy=True)
  extra_service = db.relationship("Extra_service", backref="extra-service", lazy=True)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Tenant(db.Model, UserMixin):
  __tablename__ = "Tenant"
  id = db.Column(db.Integer(), primary_key=True)
  first_name = db.Column(db.String(length=50), nullable=False)
  second_name = db.Column(db.String(length=50), nullable=False)
  last_name = db.Column(db.String(length=50), nullable=False)
  email = db.Column(db.String(length=100), nullable=False, unique=True)
  phone = db.Column(db.Integer(), nullable=False, unique=True)
  username = db.Column(db.String(length=50), nullable=False, unique=True)
  date = db.Column(db.DateTime())
  tenant_id = db.Column(db.Integer(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)
  account_type = db.Column(db.String(length=10), nullable=False)
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  properties = db.Column(db.Integer(), db.ForeignKey("Property.id"))
  unit = db.relationship("Unit", backref="unit", lazy=True)
  complaint = db.relationship("Complaints", backref="complaints", lazy=True)
  active = db.Column(db.String(length=5), nullable=False)
  bookings = db.relationship("Bookings", backref="tenant_booking", lazy=True)
  transact = db.relationship("Transaction", backref="tenant_transaction", lazy=True)
  verification = db.relationship("Verification", backref="tenant-verification", lazy=True)
  invoice = db.relationship("Invoice", backref="tenant-invoice", lazy=True)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Properties(db.Model):
  __tablename__ = "Property"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(length=50), nullable=False)
  address = db.Column(db.String(length=100), nullable=False)
  address2 = db.Column(db.String(length=100), nullable=False)
  floors = db.Column(db.Integer(), nullable=False)
  rooms = db.Column(db.Integer(), nullable=False)
  date = db.Column(db.DateTime())
  Type = db.Column(db.String(length=50), nullable=False)
  property_id = db.Column(db.Integer(), nullable=False, unique=True)
  owner = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  unit = db.relationship("Unit", backref="units", lazy=True)
  tenants = db.relationship("Tenant", backref="tenants", lazy=True)
  booking = db.relationship("Bookings", backref="property_booked", lazy=True)
  complaint = db.relationship("Complaints", backref="complaintz", lazy=True)
  transact = db.relationship("Transaction", backref="property_transaction", lazy=True)
  extra_service = db.relationship("Extra_service", backref="extras", lazy=True)
  status = db.Column(db.String(length=4), nullable=False)

class Unit(db.Model):
  __tablename__ = "Unit"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(length=50), nullable=False)
  floor = db.Column(db.Integer(), nullable=False)
  date = db.Column(db.DateTime())
  Type = db.Column(db.String(length=50), nullable=False)
  unit_id = db.Column(db.Integer(), nullable=False, unique=True)
  rent_amount = db.Column(db.Integer(), nullable=False)
  living_space = db.Column(db.Integer(), nullable=False)
  balcony_space = db.Column(db.Integer(), nullable=False)
  bedrooms = db.Column(db.Integer(), nullable=False)
  bathrooms = db.Column(db.Integer(), nullable=False)
  air_conditioning = db.Column(db.String(length=3), nullable=False)
  amenities = db.Column(db.String(length=3), nullable=False)
  unit_image = db.Column(db.String(length=50), nullable=True, default='screenshot.png')
  Property = db.Column(db.Integer(), db.ForeignKey("Property.id"))
  tenant = db.Column(db.Integer(), db.ForeignKey("Tenant.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  booking = db.relationship("Bookings", backref="unit_booked", lazy=True)
  reserved = db.Column(db.String(length=5), nullable=False)
  transact = db.relationship("Transaction", backref="unit_transaction", lazy=True)
  invoice = db.relationship("Invoice", backref="unit_invoice", lazy=True)
  extra_service = db.relationship("Extra_service", backref="extras-units", lazy=True)

class Invoice(db.Model):
  __tablename__ = 'invoices'
  id = db.Column(db.Integer(), primary_key=True)
  invoice_id = db.Column(db.Integer(), nullable=False, unique=True)
  amount = db.Column(db.Integer(), nullable=False)
  date_created = db.Column(db.DateTime(), nullable=False)
  date_closed = db.Column(db.DateTime())
  status = db.Column(db.String(10), nullable=False)
  tenant = db.Column(db.Integer(), db.ForeignKey('Tenant.id'))
  unit = db.Column(db.Integer(), db.ForeignKey('Unit.id'))
  transaction = db.relationship("Transaction",backref="transaction-invoice", lazy=True)

class Complaints(db.Model):
  __tablename__ = "Complaints"
  id = db.Column(db.Integer(), primary_key=True)
  title = db.Column(db.String(length=50), nullable=False)
  category = db.Column(db.String(length=20), nullable=False)
  body = db.Column(db.String(length=500), nullable=False)
  date = db.Column(db.Date())
  time = db.Column(db.DateTime())
  tenant = db.Column(db.Integer(), db.ForeignKey("Tenant.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  Property = db.Column(db.Integer(), db.ForeignKey("Property.id"))

class Bookings(db.Model):
  __tablename__ = "Bookings"
  id = db.Column(db.Integer(), primary_key=True)
  booking_id = db.Column(db.Integer(), nullable=False, unique=True)
  user = db.Column(db.Integer(), db.ForeignKey("members.id"))
  landlord_user = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  tenant_user = db.Column(db.Integer(), db.ForeignKey("Tenant.id"))
  date = db.Column(db.DateTime())
  expiry_date = db.Column(db.DateTime())
  property = db.Column(db.Integer(), db.ForeignKey("Property.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("Unit.id"))
  status = db.Column(db.String(length=7), nullable=False)

class Transaction(db.Model):
  __tablename__ = 'Transactions'
  id = db.Column(db.Integer(), primary_key=True)
  transaction_id = db.Column(db.Integer(), nullable=False, unique=True)
  tenant = db.Column(db.Integer(), db.ForeignKey("Tenant.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  Property = db.Column(db.Integer(), db.ForeignKey("Property.id"))
  Unit = db.Column(db.Integer(), db.ForeignKey("Unit.id"))
  invoice = db.Column(db.Integer(), db.ForeignKey('invoices.id'))
  date = db.Column(db.Date(), nullable=False)
  time = db.Column(db.DateTime(), nullable=False)
  next_date = db.Column(db.Date(), nullable=False)
  origin = db.Column(db.String(length=10), nullable=False)

class Verification(db.Model):
  __tablename__ = 'Verification'
  id = db.Column(db.Integer(), primary_key=True)
  tenant = db.Column(db.Integer(), db.ForeignKey("Tenant.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  info = db.Column(db.String(), nullable=False)
  date = db.Column(db.DateTime(), nullable=False)
  status = db.Column(db.String(length=10))

class Extras(db.Model):
  __tablename__ = 'Extras'
  id = db.Column(db.Integer(), primary_key=True)
  extra_id = db.Column(db.Integer(), nullable=False, unique=True)
  first_name = db.Column(db.String(length=80), nullable=False)
  last_name = db.Column(db.String(length=80), nullable=False)
  age = db.Column(db.Integer(), nullable=False)
  phone = db.Column(db.String(length=10), nullable=False)
  email = db.Column(db.String(length=80), nullable=False)
  title = db.Column(db.String(length=15), nullable=False)
  date = db.Column(db.DateTime(), nullable=False)
  cost = db.Column(db.Integer(), nullable=False)
  rating = db.Column(db.Integer(), nullable=False, default=0)
  extra_service = db.relationship("Extra_service", backref="extra services", lazy=True)

class Extra_service(db.Model):
  __tablename__ = 'extra_service'
  id = db.Column(db.Integer(), primary_key=True)
  extra_service_id = db.Column(db.Integer(), nullable=False, unique=True)
  landlord = db.Column(db.Integer(), db.ForeignKey("Landlord.id"))
  Property = db.Column(db.Integer(), db.ForeignKey("Property.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("Unit.id"))
  extra = db.Column(db.Integer(), db.ForeignKey("Extras.id"))
  cost = db.Column(db.Integer(), nullable=False)
  date_opened = db.Column(db.DateTime(), nullable=False)
  date_closed = db.Column(db.DateTime())
  status = db.Column(db.String(length=10), nullable=False)
