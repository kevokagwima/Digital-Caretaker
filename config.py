import os

class Config:
  SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:Hunter9039@localhost/pms"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SESSION_PERMANENT = False
  SESSION_TYPE = "filesystem"
  SECRET_KEY = os.environ.get("secret_key")
