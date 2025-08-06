import csv, random
from flask import Flask
from flask_bcrypt import Bcrypt
from Models.base_model import db
from Models.users import Tenant, Admin, Role
from Models.unit import Unit, UnitMetrics
from config import Config

app = Flask(__name__)

bcrypt = Bcrypt()
app.config.from_object(Config)
db.init_app(app)

def add_tenants():
  print("Adding Tenants...")
  f = open("download.csv")
  reader = csv.reader(f)
  for first_name, last_name, email, phone, properties, landlord, account_type in reader:
    tenant = Tenant(
      first_name=first_name,
      last_name=last_name,
      email=email,
      password=bcrypt.generate_password_hash("11111!").decode("utf-8"),
      phone=phone,
      properties=properties,
      landlord=landlord,
      account_type=account_type,
    )
    db.session.add(tenant)
    db.session.commit()
  print("Tenants Added")

def add_units():
  print("Adding units...")
  f = open("downloads.csv")
  reader = csv.reader(f)
  for name, floor, Type, Property, landlord, living_space, balcony_space, date, rent_amount in reader:
    unit = Unit(
      name=name,
      description="Discover your ideal living space in this charming 2-bedroom apartment located in the heart of Tanzania. This well-designed unit features a spacious living room that seamlessly connects to a modern kitchen, perfect for entertaining guests. Each bedroom is bright and airy, offering ample storage and comfort. Enjoy the convenience of nearby amenities, including shops, restaurants, and public transport. The apartment also boasts beautiful views of the surrounding landscape, providing a peaceful retreat after a busy day. Experience the vibrant culture of Tanzania while enjoying the comforts of home!",
      alias=name.replace(" ", "-").replace("/", "-").replace(".", "-").replace(",", "-").replace("_", "-"),
      unit_floor=floor,
      unit_type=Type,
      landlord=landlord,
      properties=Property,
      date_added=date,
      rent_amount=rent_amount,
    )
    db.session.add(unit)
    db.session.commit()
    unit_metric = UnitMetrics(
      living_space=living_space,
      balcony_space=balcony_space,
      bedrooms=2,
      bathrooms=1,
      unit = unit.id
    )
    db.session.add(unit_metric)
    db.session.commit()
  print("Units added")

def add_admin():
  new_admin = Admin(
    first_name = "Admin",
    last_name = "Admin",
    email = "admin@gmail.com",
    phone = 796897011,
    passwords = "12345",
    account_type = Role.query.filter_by(name="Admin").first().id
  )
  db.session.add(new_admin)
  db.session.commit()

if __name__ == '__main__':
  with app.app_context():
    add_tenants()
    add_units()
    add_admin()
