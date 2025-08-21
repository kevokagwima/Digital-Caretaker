from Models.base_model import db, BaseModel

class Subscription(BaseModel, db.Model):
  __tablename__ = "subscription"
  amount = db.Column(db.Integer())
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  payment = db.relationship("Payment", backref="subscription_payment", lazy=True, cascade="all, delete, delete-orphan", passive_deletes=True)

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
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  subscription_id = db.Column(db.Integer, db.ForeignKey("subscription.id"))

  def __repr__(self):
    return f"Payment(MerchantRequestID={self.MerchantRequestID}, CheckoutRequestID={self.CheckoutRequestID}, amount={self.amount}, invoice={self.invoice})"

