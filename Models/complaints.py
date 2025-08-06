from Models.base_model import db, BaseModel

class Complaints(BaseModel, db.Model):
  __tablename__ = "complaints"
  title = db.Column(db.String(50), nullable=False)
  category = db.Column(db.String(20), nullable=False)
  message = db.Column(db.Text(), nullable=False)
  tenant_id = db.Column(db.Integer(), db.ForeignKey("tenant.id"))
  landlord_id = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))

  def __repr__(self):
    return f"{self.title} - {self.category}"
