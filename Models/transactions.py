from Models.base_model import db, BaseModel

class Transactions(BaseModel, db.Model):
  __tablename__ = 'transactions'
  tenant = db.Column(db.Integer(), db.ForeignKey("tenant.id"))
  landlord = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  properties = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  unit = db.Column(db.Integer(), db.ForeignKey("unit.id"))
  invoice = db.Column(db.Integer(),db. ForeignKey('invoice.id'))
  date = db.Column(db.Date(), nullable=False)
  time = db.Column(db.DateTime(), nullable=False)
  next_date = db.Column(db.Date(), nullable=False)
  origin = db.Column(db.String(10), nullable=False)

  def __repr__(self):
    return f"Transaction(tenant={self.tenant}, landlord={self.landlord}, date={self.date}, origin={self.origin})"
