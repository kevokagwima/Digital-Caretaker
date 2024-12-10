from app import create_app
from Models.base_model import db
from Models.bookings import *
from Models.complaints import *
from Models.extras import *
from Models.invoice import *
from Models.property import *
from Models.transactions import *
from Models.unit import *
from Models.users import Role
from Models.property import PropertyTypes

app = create_app()

def drop_tables():
  print("Dropping tables...")
  db.drop_all()
  print("Tables Dropped")

def create_tables():
  print("Creating tables...")
  db.create_all()
  print("Tables Created")

def add_roles():
  new_role = Role(
    name = "Admin"
  )
  db.session.add(new_role)
  db.session.commit()
  print(f"Added role {new_role.name}")
  new_role = Role(
    name = "Member"
  )
  db.session.add(new_role)
  db.session.commit()
  print(f"Added role {new_role.name}")
  new_role = Role(
    name = "Landlord"
  )
  db.session.add(new_role)
  db.session.commit()
  print(f"Added role {new_role.name}")
  new_role = Role(
    name = "Tenant"
  )
  db.session.add(new_role)
  db.session.commit()
  print(f"Added role {new_role.name}")

def add_property_types():
  new_property_type = PropertyTypes(
    name = "Apartment"
  )
  db.session.add(new_property_type)
  db.session.commit()
  print(f"Added property type: {new_property_type.name}")

if __name__ == "__main__":
  with app.app_context():
    # drop_tables()
    create_tables()
    # add_roles()
    # add_property_types()
