from Models.base_model import db, BaseModel

class PropertyTypes(BaseModel, db.Model):
  __tablename__ = 'property_types'
  name = db.Column(db.String(30), nullable=False)
  properties = db.relationship("Property", backref="properties", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

  def __repr__(self):
    return f"{self.name}"

class Property(BaseModel, db.Model):
  __tablename__ = "property"
  name = db.Column(db.String(100), nullable=False)
  alias = db.Column(db.String(100), nullable=False)
  property_floors = db.Column(db.Integer(), nullable=False)
  rooms = db.Column(db.Integer(), nullable=False)
  property_type = db.Column(db.Integer(), db.ForeignKey("property_types.id"))
  property_location = db.relationship("PropertyLocation", backref="properties", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

  
  def __repr__(self):
    return f"{self.name}"

class PropertyLocation(BaseModel, db.Model):
  __tablename__ = "property_location"
  county = db.Column(db.String(50), nullable=False)
  city = db.Column(db.String(50), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("property.id"))
  
  def __repr__(self):
    return f"{self.county}, {self.city}"
