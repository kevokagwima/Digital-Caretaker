from Models.base_model import db, BaseModel, get_local_time
from Models.transactions import Transactions, Payment

class Invoice(BaseModel, db.Model):
  __tablename__ = 'invoice'
  amount = db.Column(db.Integer(), nullable=False)
  month_created = db.Column(db.Date(), nullable=False)
  date_closed = db.Column(db.DateTime())
  status = db.Column(db.String(10), nullable=False)
  tenant_id = db.Column(db.Integer(), db.ForeignKey('tenant.id'))
  unit_id = db.Column(db.Integer(), db.ForeignKey('unit.id'))
  transaction = db.relationship("Transactions",backref="transaction_invoice", lazy=True, cascade="all, delete, delete-orphan")
  payment = db.relationship("Payment",backref="payment_invoice", lazy=True, cascade="all, delete, delete-orphan")

  def __repr__(self):
    return f"{self.amount} - {self.status}"
