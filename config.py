import os

class Config:
  SQLALCHEMY_DATABASE_URI = "mssql://@KEVINKAGWIMA/project?driver=SQL SERVER"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECRET_KEY = os.environ['Hms_secret_key']
  SESSION_PERMANENT = False
  SESSION_TYPE = "filesystem"
  GOOGLEMAPS_KEY = os.environ['Google_maps']
  UPLOAD_FOLDER = 'Static/css/Images/Screenshots'
  UPLOAD_FOLDER = UPLOAD_FOLDER
