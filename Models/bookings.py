from Models.base_model import db, BaseModel

class Bookings(BaseModel, db.Model):
  __tablename__ = "Bookings"
  user = db.Column(db.String(50))
  date = db.Column(db.DateTime())
  expiry_date = db.Column(db.DateTime())
  property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("unit.id"))
  status = db.Column(db.String(10), nullable=False)

  def __repr__(self):
    return f"{self.user}"
