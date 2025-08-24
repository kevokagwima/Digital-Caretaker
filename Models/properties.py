from Models.base_model import db, BaseModel

class PropertyTypes(BaseModel, db.Model):
  __tablename__ = 'property_types'
  name = db.Column(db.String(30), nullable=False)
  properties = db.relationship("Property", backref="property_types", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

  def __repr__(self):
    return f"{self.name}"

class Property(BaseModel, db.Model):
  __tablename__ = "property"
  name = db.Column(db.String(100), nullable=False)
  alias = db.Column(db.String(100), nullable=False)
  property_type_id = db.Column(db.Integer(), db.ForeignKey("property_types.id"))
  owner_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
  property_amenities = db.relationship("PropertyAmenities", backref="property_amenities", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)
  property_location = db.relationship("PropertyLocation", backref="property_location", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)
  property_images = db.relationship("PropertyImages", backref="property_images", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)
  
  def __repr__(self):
    return f"{self.name}"

class PropertyAmenities(BaseModel, db.Model):
  __tablename__ = "property_amenities"
  name = db.Column(db.String(100), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("property.id"))
  
  def __repr__(self):
    return f"{self.name}"

class PropertyLocation(BaseModel, db.Model):
  __tablename__ = "property_location"
  county = db.Column(db.String(50), nullable=False)
  city = db.Column(db.String(50), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("property.id"))
  
  def __repr__(self):
    return f"{self.county}, {self.city}"

class PropertyImages(BaseModel, db.Model):
  __tablename__ = "property_images"
  image_name = db.Column(db.String(50), nullable=False)
  property_id = db.Column(db.Integer(), db.ForeignKey("property.id"))
  
  def __repr__(self):
    return f"{self.image_name}"
