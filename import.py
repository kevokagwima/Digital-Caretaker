import csv, random
from flask import Flask
from flask_bcrypt import Bcrypt
from models import *
from config import Config

app = Flask(__name__)

bcrypt = Bcrypt()
app.config.from_object(Config)
db.init_app(app)

def main():
  f = open("download.csv")
  reader = csv.reader(f)
  # for first_name, second_name, last_name, email, username, password, phone, properties, landlord, account_type, active, date in reader:
  #   tenant = Tenant(
  #     first_name=first_name,
  #     second_name=second_name,
  #     last_name=last_name,
  #     email=email,
  #     username=username,
  #     password=bcrypt.generate_password_hash(password).decode("utf-8"),
  #     phone=phone,
  #     properties=properties,
  #     landlord=landlord,
  #     account_type=account_type,
  #     active=active,
  #     date=date,
  #     tenant_id=random.randint(100000,999999)
  #   )
  #   db.session.add(tenant)
  #   db.session.commit()
  for name, floor, type, landlord, Property, living_space, balcony_space, air_conditioning, amenities, reserved, date, unit_id, rent_amount, tenant in reader:
    unit = Unit(
      name=name,
      floor=floor,
      Type=type,
      landlord=landlord,
      Property=Property,
      living_space=living_space,
      balcony_space=balcony_space,
      bedrooms=0,
      bathrooms=0,
      air_conditioning=air_conditioning,
      amenities=amenities,
      reserved=reserved,
      date=date,
      unit_id=unit_id,
      rent_amount=rent_amount
    )
    db.session.add(unit)
    db.session.commit()
    if tenant:
      unit.tenant = tenant
      db.session.commit()
    else:
      pass



if __name__ == '__main__':
  with app.app_context():
    main()
