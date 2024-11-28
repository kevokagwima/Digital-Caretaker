from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

db = SQLAlchemy()

class BaseModel(db.Model):
  __abstract__ = True
  id = db.Column(db.Integer(), nullable=False, primary_key=True)
  unique_id = db.Column(db.Integer(), unique=True, nullable=False)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.unique_id = random.randint(100000, 999999)

  def __repr__(self):
    return f"{self.id} - {self.unique_id}"

class UserBaseModel(db.Model):
  __abstract__ = True
  first_name = db.Column(db.String(50), nullable=False)
  last_name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(100), nullable=False, unique=True)
  phone = db.Column(db.Integer(), nullable=False, unique=True)
  password = db.Column(db.String(80), nullable=False)
  date = db.Column(db.DateTime())

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.date = datetime.now()

  def __repr__(self):
    return f"{self.first_name} {self.first_name}"
