from Models.base_model import db, BaseModel

class Payment(BaseModel, db.Model):
  __tablename__ = "payment"
  MerchantRequestID = db.Column(db.String(50))
  CheckoutRequestID = db.Column(db.String(50))
  MpesaReceiptNumber = db.Column(db.String(20))
  transactionDate = db.Column(db.DateTime())
  amount = db.Column(db.Integer())
  phone_number = db.Column(db.String(20))
  is_pending = db.Column(db.Boolean(), default=True)
  is_confirmed = db.Column(db.Boolean(), default=False)
  is_failed = db.Column(db.Boolean(), default=False)
  invoice = db.Column(db.Integer, db.ForeignKey("invoice.id"))

  def __repr__(self):
    return f"Payment(MerchantRequestID={self.MerchantRequestID}, CheckoutRequestID={self.CheckoutRequestID}, amount={self.amount}, invoice={self.invoice})"

class Transactions(BaseModel, db.Model):
  __tablename__ = 'transactions'
  tenant_id = db.Column(db.Integer(), db.ForeignKey("tenant.id"))
  landlord_id = db.Column(db.Integer(), db.ForeignKey("landlord.id"))
  property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))
  unit_id = db.Column(db.Integer(), db.ForeignKey("unit.id"))
  invoice_id = db.Column(db.Integer(),db. ForeignKey('invoice.id'))
  payment_method = db.Column(db.String(10), nullable=False)
  next_date = db.Column(db.Date(), nullable=False)

  def __repr__(self):
    return f"Transaction(tenant={self.tenant}, landlord={self.landlord}, date={self.date_created}, origin={self.payment_method})"
