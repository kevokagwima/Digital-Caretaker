import os

class Config:
  SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://KEVINKAGWIMA/pms?driver=ODBC+Driver+17+for+SQL+Server"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SESSION_PERMANENT = False
  SESSION_TYPE = "filesystem"
  SECRET_KEY = os.environ.get("SECRET_KEY")
