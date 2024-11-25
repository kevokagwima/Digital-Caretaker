import csv, random
from flask import Flask
from flask_bcrypt import Bcrypt
from Models.models import *
from config import Config

app = Flask(__name__)

bcrypt = Bcrypt()
app.config.from_object(Config)
db.init_app(app)

def main():
  f = open("download.csv")
  reader = csv.reader(f)
  for first_name, last_name, email, phone, properties, landlord, account_type, date in reader:
    tenant = Tenant(
      first_name=first_name,
      last_name=last_name,
      email=email,
      password=bcrypt.generate_password_hash("11111").decode("utf-8"),
      phone=phone,
      properties=properties,
      landlord=landlord,
      account_type=account_type,
      date=date,
      unique_id=random.randint(100000,999999)
    )
    db.session.add(tenant)
    # db.session.commit()
  # for name, floor, Type, Property, landlord, living_space, balcony_space, air_conditioning, amenities, reserved, date, rent_amount in reader:
  #   unit = Unit(
  #     name=name,
  #     floor=floor,
  #     Type=Type,
  #     landlord=landlord,
  #     Property=Property,
  #     living_space=living_space,
  #     balcony_space=balcony_space,
  #     bedrooms=3,
  #     bathrooms=3,
  #     air_conditioning=air_conditioning,
  #     amenities=amenities,
  #     reserved=reserved,
  #     date=date,
  #     unit_id=random.randint(100000,999999),
  #     rent_amount=rent_amount
  #   )
  #   db.session.add(unit)
  #   db.session.commit()

def admin():
  new_admin = Admin(
    unique_id = random.randint(100000,999999),
    passwords = "11111",
  )
  db.session.add(new_admin)
  db.session.commit()
  print("Admin added")

if __name__ == '__main__':
  with app.app_context():
    admin()
    # main()
