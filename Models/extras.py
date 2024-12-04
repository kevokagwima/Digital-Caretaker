from Models.base_model import db, BaseModel, UserBaseModel

class Extras(BaseModel, UserBaseModel, db.Model):
  __tablename__ = "extras"
  age = db.Column(db.Integer(), nullable=False)
  title = db.Column(db.String(15), nullable=False)
  rate = db.Column(db.Integer(), nullable=False)
  rating = db.Column(db.Integer(), nullable=False, default=0)
  extra_service = db.relationship("ExtraService", backref="extra services", lazy=True, cascade="all, delete, delete-orphan")

  def __repr__(self):
    return f"{self.first_name} {self.last_name} - {self.title}"

class ExtraService(BaseModel, db.Model):
  __tablename__ = 'extra_service'
  landlord = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  Property = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("unit.id"))
  extra = db.Column(db.Integer(), db.ForeignKey("extras.id"))
  cost = db.Column(db.Integer(), nullable=False)
  date_opened = db.Column(db.DateTime(), nullable=False)
  date_closed = db.Column(db.DateTime())
  status = db.Column(db.String(10), nullable=False)

  def __repr__(self):
    return f"{self.extra} - {self.cost}"
