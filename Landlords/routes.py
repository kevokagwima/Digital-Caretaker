from flask import Blueprint, render_template, flash, url_for, redirect, request, session, abort, jsonify, json
from flask_login import login_required, current_user
from Models.models import db, Landlord, Tenant, Unit, Properties, Extras, Transaction, Users, Complaints, Extra_service, Invoice, UnitImage
from .form import PropertyRegistrationForm, UnitRegistrationForm
from modules import check_reservation_expiry, assign_tenant_unit, revoke_tenant_access
from datetime import date, datetime
import random, boto3, asyncio, aiohttp, os

landlords = Blueprint("landlord", __name__, url_prefix="/landlord")
s3 = boto3.resource(
  "s3",
  aws_access_key_id = os.environ.get("aws_access_key"),
  aws_secret_access_key = os.environ.get("aws_secret_key")
)
client = boto3.client(
  "s3",
  aws_access_key_id = os.environ.get("aws_access_key"),
  aws_secret_access_key = os.environ.get("aws_secret_key")
)
bucket_name = os.environ.get("bucket_name")
region = os.environ.get("region")
today = date.today()

@landlords.route("/dashboard", methods=["POST", "GET"])
@login_required
def landlord_dashboard():
  if current_user.account_type != "Landlord":
    abort(403)
  properties = db.session.query(Properties).filter(current_user.id == Properties.owner).all()
  tenants = db.session.query(Tenant).filter(Tenant.landlord == current_user.id).all()
  todays_time = datetime.now().strftime("%d/%m/%Y")
  if session.get("this_month"):
    this_month = datetime.strptime(session["this_month"], '%Y-%m-%d').date()
  else:
    this_month = today
  extras = Extras.query.all()
  active_extras = Extra_service.query.filter(Extra_service.landlord == current_user.id).all()
  units = Unit.query.filter(Unit.landlord == current_user.id).all()
  invoices = Invoice.query.filter_by(status="Cleared").order_by(Invoice.date_closed.desc()).all()
  

  context = {
    "properties": properties,
    "tenants": tenants,
    "todays_time": todays_time,
    "active_extras": active_extras,
    "units": units,
    "invoices": invoices,
    "extras": extras,
    "this_month": this_month
  }

  return render_template("new_dash.html", **context)

@landlords.route("/property-information/<int:property_id>", methods=["POST","GET"])
@login_required
def property_information(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  # try:
  propertiez = Properties.query.get(property_id)
  properties = db.session.query(Properties).filter(current_user.id == Properties.owner).all()
  if propertiez.owner != current_user.id:
    flash(f"Unknown Property", category="info")
    return redirect(url_for("landlord.landlord_dashboard"))
  all_users = []
  member_users = Users.query.all()
  tenant_users = Tenant.query.all()
  landlord_users = Landlord.query.all()
  for members in member_users:
    all_users.append(members)
  for tenantz in tenant_users:
    all_users.append(tenantz)
  for landlord in landlord_users:
    all_users.append(landlord)
  today_time = datetime.now().strftime("%d/%m/%Y")
  # session["property"] = propertiez
  tenants = db.session.query(Tenant).filter(Tenant.properties == propertiez.id).all()
  units = db.session.query(Unit).filter(Unit.Property == propertiez.id).all()
  
  all_complaints = Complaints.query.filter_by(Property=propertiez.id).order_by(Complaints.date.desc()).all()
  check_reservation_expiry(propertiez.id)
  # except Exception as e:
  #   flash(f"{repr(e)}", category="warning")
  #   return redirect(url_for("landlord.landlord_dashboard"))

  context = {
    "propertiez": propertiez,
    "properties": properties,
    "tenants": tenants,
    "units": units,
    "all_complaints": all_complaints,
    "all_users": all_users,
    "this_month": today
  }

  return render_template("property_dashboard.html", **context)

@landlords.route("/tenant-profile/<int:tenant_id>", methods=["GET", "POST"])
@login_required
def tenant_details(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    today_time = datetime.now().strftime("%d/%m/%Y")
    tenant = Tenant.query.get(tenant_id)
    tenant_property = Properties.query.filter_by(id=tenant.properties).first()
    if tenant.landlord != current_user.id:
      flash(f"Unknown Tenant ID", category="info")
      return redirect(url_for("landlord.landlord_dashboard"))
    complaints = Complaints.query.filter_by(tenant=tenant.id).all()
    all_complaints = Complaints.query.filter_by(Property=tenant_property.id).order_by(Complaints.date.desc()).all()
    transactions = Transaction.query.filter_by(tenant=tenant.id).all()
    units = Unit.query.all()
    tenant_invoices = Invoice.query.filter_by(tenant=tenant.id).all()
    
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

  return render_template("tenant_details.html",tenant=tenant,complaints=complaints,units=units, today_time=today_time, tenant_property=tenant_property, tenant_invoices=tenant_invoices, transactions=transactions, all_complaints=all_complaints)

@landlords.route("/send-message/<int:tenant_id>", methods=["POST","GET"])
@login_required
def send_message(tenant_id):
  tenant = Tenant.query.get(tenant_id)
  flash("Functionality in progress", category="info")
  return redirect(url_for('landlord.tenant_details', tenant_id=tenant.id))

@landlords.route("/assign-tenant-unit/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def assign_unit_now(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
      flash("Tenant not found", category="danger")
      return redirect(url_for('landlord.landlord_dashboard'))
    unit_id = request.form.get("unit-assign")
    unit = Unit.query.get(unit_id)
    if not unit:
      flash("Unit not found", category="danger")
    elif tenant.unit:
      flash("Tenant already has a unit assigned to him", category="danger")
    elif unit.tenant:
      flash("Unit already occupied", category="danger")
    else:
      assign_tenant_unit(tenant_id, unit_id)

    return redirect(url_for('landlord.tenant_details', tenant_id=tenant_id))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('landlord.tenant_details', tenant_id=tenant_id))

@landlords.route("/revoke-tenant/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def remove_tenant_now(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
      flash("Tenant not found", category="danger")
    elif tenant.is_active == False:
      flash("Tenant's already revoked", category="info")
    else:
      tenant_property = tenant.properties
      revoke_tenant_access(tenant_id)
  except Exception as e:
    flash(f"{repr(e)}", category="danger")

  return redirect(url_for("landlord.property_information", property_id=tenant_property))

@landlords.route("/property-registration", methods=["POST", "GET"])
@login_required
def add_property():
  form = PropertyRegistrationForm()
  if form.validate_on_submit():
    new_property = Properties(
      name = form.name.data,
      address = form.county.data,
      address2 = form.city.data,
      floors = form.floors.data,
      rooms = form.total_units.data,
      Type = form.property_type.data,
      property_id = random.randint(100000, 999999),
      date = datetime.now(),
      owner = current_user.id,
    )
    existing_property = Properties.query.filter_by(name=new_property.name, owner=current_user.id).first()
    if existing_property:
      flash(f"A property with the name {existing_property.name} already exists", category="warning")
    else:
      db.session.add(new_property)
      db.session.commit()
      flash(f"Property {new_property.name}  was created successfully",category="success")
      return redirect(url_for('landlord.property_information', property_id=new_property.id))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")

  return render_template("property-registration.html", form=form)

@landlords.route("/update-property/<int:property_id>", methods=["POST", "GET"])
@login_required
def edit_property(property_id):
  try:
    form = PropertyRegistrationForm()
    edit_property = Properties.query.get(property_id)
    if edit_property.owner != current_user.id:
      flash("You do not have permission to edit this property.", category="danger")
      return redirect(url_for('landlord.landlord_dashboard'))
    if form.validate_on_submit():
      if form.name.data != edit_property.name:
        existing_property = Properties.query.filter_by(name=form.name.data, owner=current_user.id).first()
        if existing_property:
          flash(f"A property with the name {existing_property.name} already exists", category="warning")
      else:
        edit_property.floors = form.floors.data,
        db.session.commit()
        flash(f"Property {edit_property.name}  updated successfully",category="success")
      return redirect(url_for('landlord.property_information', property_id=edit_property.id))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")
  
    return render_template("edit-property.html", form=form, property=edit_property)

  except Exception as e:
    flash(f"An error occurred: {repr(e)}", category="danger")
    db.session.rollback()
    return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/delete-property/<int:property_id>", methods=["POST", "GET"])
@login_required
def delete_property(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    landlord_property = Properties.query.get(property_id)
    if not landlord_property:
      flash("Property not found", category="danger")
    elif landlord_property.tenants or landlord_property.unit:
      flash(f"Cannot remove {landlord_property.name}. Some units are occupied",category="danger")
      return redirect(url_for("landlord.property_information", property_id=landlord_property.id))
    elif landlord_property.owner != current_user.id:
      flash(f"No property with the name {landlord_property.name}",category="danger")
    else:
      db.session.delete(landlord_property)
      for unit in landlord_property.unit:
        db.session.delete(unit)
      db.session.commit()
      flash(f"Property {landlord_property.name} has been removed successfully",category="success",)
    return redirect(url_for("landlord.landlord_dashboard"))

  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

@landlords.route("/add-unit/<int:property_id>", methods=["POST", "GET"])
@login_required
def add_unit(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  form = UnitRegistrationForm()
  current_property = Properties.query.filter_by(property_id=property_id).first()
  # try:
  if form.validate_on_submit():
    new_unit = Unit(
      unit_id = random.randint(100000, 999999),
      name = form.name.data,
      floor = form.floor.data,
      Type = form.unit_type.data,
      date = datetime.now(),
      rent_amount = form.rent_amount.data,
      living_space = form.living_room_space.data,
      balcony_space = form.balcony_room_space.data,
      bedrooms = form.bedrooms.data,
      bathrooms = form.bathrooms.data,
      Property = current_property.id,
      landlord = current_user.id
    )

    if check_if_unit_exists(current_property.id, new_unit.name):
      return redirect(url_for('landlord.property_information',property_id=current_property.id))
    if check_if_floor_exists(current_property.id, new_unit.floor):
      return redirect(url_for('landlord.property_information',property_id=current_property.id))
    if check_if_property_is_full(current_property.id):
      return redirect(url_for('landlord.property_information',property_id=current_property.id))

    files = request.files.getlist("unit_image")
    db.session.add(new_unit)
    db.session.commit()
    asyncio.run(upload_file(new_unit.id, files, property_id))
    flash(f"Unit {new_unit.name} - {new_unit.Type} Added successfully",category="success")
    return redirect(url_for('landlord.property_information',property_id=current_property.id))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")

  return render_template("unit-registration.html", form=form)
  # except:
  #   flash(f"Something went wrong. Try again later", category="danger")
  #   return redirect(url_for("landlord.property_information", property_id=this_property.id))

def check_if_unit_exists(property_id, new_unit_name):
  current_property = Properties.query.get(property_id)
  unit = Unit.query.filter_by(name=new_unit_name, Property=property_id).first()
  if unit:
    flash(f"A unit with name {new_unit_name} already exists in {current_property.name}", category="warning")
    return True

def check_if_floor_exists(property_id, new_unit_floor):
  current_property = Properties.query.get(property_id)
  if new_unit_floor > current_property.floors or new_unit_floor < 0:
    flash(f"Floor {new_unit_floor} does not exist", category="danger")
    return True

def check_if_property_is_full(property_id):
  current_property = Properties.query.get(property_id)
  units = Unit.query.filter_by(Property=property_id).all()
  if len(units) >= current_property.rooms:
    flash(f"Maximum units allowed of this property has been reached", category="warning")
    return False

async def upload_file(unit_id, property_id, files):
  if files:
    unit = Unit.query.filter_by(unit_id=unit_id).first()
    unit_property = Properties.query.filter_by(property_id=property_id).first()
    for file in files:
      unit_image = UnitImage(
        name = file.filename,
        bucket = bucket_name,
        region = region,
        unit = unit.id
      )
      db.session.add(unit_image)
      db.session.commit()
      try:
        async with aiohttp.ClientSession() as session:
          async with session.put(f"s3://{bucket_name}/{file.filename}", data=file.read()) as response:
            if response.status == 200:
              flash("Images uploaded successfully", category="success")
            else:
              flash("Failed to upload images", category="danger")
      except Exception as e:
        flash(f"{repr(e)}", category="danger")

@landlords.route("/update-property-availability/<int:property_id>", methods=["POST", "GET"])
@login_required
def update_property_availability(property_id):
  this_property = session["property"]
  Property = Properties.query.get(property_id)
  availability = request.form.get("availability")
  Property.status = availability
  units = Unit.query.filter_by(Property=Property.id, tenant=None).all()
  if availability == "Sale":
    for unit in units:
      unit.rent_amount = unit.rent_amount * 50
  if availability == "Rent":
    for unit in units:
      unit.rent_amount = unit.rent_amount / 50
  db.session.commit()
  flash(f"{Property.name} availability has been updated successfully. The units rent amount have been adjusted", category="success")

  return redirect(url_for("landlord.property_information", property_id=this_property.id))

@landlords.route("/extra-service/<string:extra_type>", methods=["POST", "GET"])
@login_required
def extra_service(extra_type):
  if current_user.account_type != "Landlord":
    abort(403)
  extras = Extras.query.filter_by(title=extra_type).all()
  properties = Properties.query.filter(Properties.owner == current_user.id).all()
  units = Unit.query.filter(Unit.landlord == current_user.id).all()

  return render_template("extra_services.html", extras=extras, extra_type=extra_type, properties=properties, units=units)

@landlords.route("/extra-services/<int:property_id>", methods=["POST", "GET"])
@login_required
def unit_select(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  units = Unit.query.filter_by(Property=property_id).all()
  unitsArray = []
  for unit in units:
    unitObj = {}
    unitObj["id"] = unit.id  
    unitObj["name"] = unit.name  
    unitObj["type"] = unit.Type
    unitsArray.append(unitObj)

  return jsonify({'units': unitsArray})

@landlords.route("/extra-service/<int:extra_id>", methods=["POST", "GET"])
@login_required
def select_extra_service(extra_id):
  if current_user.account_type != "Landlord":
    abort(403)
  if request.get_data('data'):
    data = json.loads(request.get_data('data'))
  extra = Extras.query.filter_by(id=data.get("extra")).first()
  active_extras = Extra_service.query.filter(Extra_service.landlord == current_user.id, Extra_service.status == "Ongoing", Extra_service.extra == extra_id).all()
  if active_extras:
    extra_occupancy(extra_id)
  else:
    try:
      new_service = Extra_service(
        extra_service_id = random.randint(100000, 999999),
        landlord = current_user.id,
        Property = data.get("property"),
        unit = data.get("unit"),
        extra = data.get("extra"),
        date_opened = datetime.now(),
        cost = extra.cost * 5,
        status = "Ongoing"
      )
      db.session.add(new_service)
      db.session.commit()
      extra_occupancy(extra.id)
    except:
      flash(f"Could not dispatch the extra to your property", category="danger")
      return redirect(url_for("landlord.extra_service", extra_type=extra.title))

  return redirect(url_for("landlord.landlord_dashboard"))

@landlords.route("/extra-occupancy/<int:extra_id>", methods=["POST", "GET"])
@login_required
def extra_occupancy(extra_id):
  if current_user.account_type != "Landlord":
    abort(403)
  extra = Extras.query.get(extra_id)
  active_extras = Extra_service.query.filter_by(landlord = current_user.id, status="Ongoing", extra=extra.id).all()
  occupied_extras = []
  for extras in active_extras:
    occupied_extras.append(extras.extra)
  occupyInfo = {}
  occupyInfo["fname"] = extra.first_name 
  occupyInfo["lname"] = extra.last_name
  if extra.id in occupied_extras:
    return jsonify({'message': occupyInfo})
  else:
    return jsonify({'messages': occupyInfo})

@landlords.route("/delete-extra-service/<int:extra_service_id>")
@login_required
def delete_extra_service(extra_service_id):
  maintenance = Extra_service.query.get(extra_service_id)
  if maintenance:
    db.session.delete(maintenance)
    db.session.commit()
    flash("Maintenance deleted successfully", category="success")
    return redirect(url_for('landlord.landlord_dashboard'))
  else:
    flash("Maitenance not found", category="danger")
    return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/maintenance-complete/<int:extra_service_id>")
@login_required
def complete_extra_service(extra_service_id):
  maintenance = Extra_service.query.get(extra_service_id)
  if maintenance:
    maintenance.date_closed = datetime.now()
    maintenance.status = "Closed"
    db.session.commit()
    flash(f"Maintenance #{maintenance.extra_service_id} marked as complete", category="success")
  else:
    flash("Maintenance record not found", category="danger")

  return redirect(url_for('landlord.landlord_dashboard'))
