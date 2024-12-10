from flask import Blueprint, render_template, flash, url_for, redirect, request, session, jsonify, json
from flask_login import login_required, current_user
from Models.base_model import db
from Models.users import Landlord, Tenant, Users
from Models.unit import Unit, UnitImage, UnitMetrics
from Models.property import Properties, PropertyTypes, UnitTypes
from Models.transactions import Transactions
from Models.complaints import Complaints
from Models.extras import Extras, ExtraService
from Models.invoice import Invoice
from .form import PropertyRegistrationForm, UnitRegistrationForm, UnitMetricRegistrationForm, UnitTypeForm
from decorators import landlord_role_required
from modules import check_reservation_expiry, assign_tenant_unit, revoke_tenant_access
from .aws_credentials import awsCredentials
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import date, datetime
import random, boto3, asyncio

landlords = Blueprint("landlord", __name__, url_prefix="/landlord")
client = boto3.client(
  "s3",
  aws_access_key_id = awsCredentials.aws_access_key,
  aws_secret_access_key = awsCredentials.aws_secret_key
)
s3 = boto3.resource(
  "s3",
  aws_access_key_id = awsCredentials.aws_access_key,
  aws_secret_access_key = awsCredentials.aws_secret_key
)
bucket_name = awsCredentials.bucket_name
region = awsCredentials.region
today = date.today()

@landlords.route("/dashboard", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def landlord_dashboard():
  properties = db.session.query(Properties).filter(current_user.id == Properties.property_owner).all()
  tenants = Tenant.query.filter_by(landlord = current_user.id).all()
  todays_time = datetime.now().strftime("%d/%m/%Y")
  if session.get("this_month"):
    this_month = datetime.strptime(session["this_month"], '%Y-%m-%d').date()
  else:
    this_month = today
  extras = Extras.query.all()
  active_extras = ExtraService.query.filter(ExtraService.landlord == current_user.id).all()
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

  return render_template("Landlord/new_dash.html", **context)

@landlords.route("/property/dashboard/<int:property_id>", methods=["POST","GET"])
@login_required
@landlord_role_required("Landlord")
def property_information(property_id):
  try:
    form = UnitTypeForm()
    propertiez = Properties.query.filter_by(unique_id=property_id, property_owner=current_user.id).first()
    if not propertiez:
      flash(f"Property not found", category="info")
      return redirect(url_for("landlord.landlord_dashboard"))
    properties = db.session.query(Properties).filter(current_user.id == Properties.property_owner).all()
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
    tenants = db.session.query(Tenant).filter(Tenant.properties == propertiez.id).all()
    units = db.session.query(Unit).filter(Unit.properties == propertiez.id).all()
    all_complaints = Complaints.query.filter_by(properties=propertiez.id).order_by(Complaints.date.desc()).all()
    check_reservation_expiry(propertiez.id)

    context = {
      "propertiez": propertiez,
      "properties": properties,
      "tenants": tenants,
      "units": units,
      "all_complaints": all_complaints,
      "all_users": all_users,
      "this_month": today,
      "form": form
    }

    return render_template("Landlord/property_dashboard.html", **context)

  except Exception as e:
    flash(f"{repr(e)}", category="warning")
    return redirect(url_for("landlord.landlord_dashboard"))

@landlords.route("/tenant-profile/<int:tenant_id>", methods=["GET", "POST"])
@login_required
@landlord_role_required("Landlord")
def tenant_details(tenant_id):
  try:
    today_time = datetime.now().strftime("%d/%m/%Y")
    tenant = Tenant.query.get(tenant_id)
    tenant_property = Properties.query.filter_by(id=tenant.properties).first()
    if tenant.landlord != current_user.id:
      flash(f"Unknown Tenant ID", category="info")
      return redirect(url_for("landlord.landlord_dashboard"))
    complaints = Complaints.query.filter_by(tenant=tenant.id).all()
    all_complaints = Complaints.query.filter_by(properties=tenant_property.id).order_by(Complaints.date.desc()).all()
    transactions = Transactions.query.filter_by(tenant=tenant.id).all()
    units = Unit.query.all()
    tenant_invoices = Invoice.query.filter_by(tenant=tenant.id).all()

    return render_template("Landlord/tenant_details.html",tenant=tenant,complaints=complaints,units=units, today_time=today_time, tenant_property=tenant_property, tenant_invoices=tenant_invoices, transactions=transactions, all_complaints=all_complaints)
    
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

@landlords.route("/send-message/<int:tenant_id>", methods=["POST","GET"])
@login_required
@landlord_role_required("Landlord")
def send_message(tenant_id):
  tenant = Tenant.query.get(tenant_id)
  flash("Feature coming soon", category="info")
  return redirect(url_for('landlord.tenant_details', tenant_id=tenant.id))

@landlords.route("/assign-tenant-unit/<int:tenant_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def assign_unit_now(tenant_id):
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

@landlords.route("/remove-tenant/<int:tenant_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def remove_tenant_now(tenant_id):
  try:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
      flash("Tenant not found", category="danger")
    elif tenant.is_active == False:
      flash("Tenant's already removed", category="info")
    else:
      tenant_property = Properties.query.get(tenant.properties)
      revoke_tenant_access(tenant_id)
      return redirect(url_for("landlord.property_information", property_id=tenant_property.unique_id))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

  return redirect(url_for("landlord.property_information", property_id=tenant_property.unique_id))

@landlords.route("/property-registration", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def add_property():
  form = PropertyRegistrationForm()
  if form.validate_on_submit():
    new_property = Properties(
      name = form.name.data,
      county = form.county.data,
      city = form.city.data,
      property_floors = form.floors.data,
      rooms = form.total_units.data,
      property_type = PropertyTypes.query.filter_by(name=form.property_type.data).first().id,
      date_added = datetime.now(),
      property_owner = current_user.id,
    )
    existing_property = Properties.query.filter_by(name=new_property.name, property_owner=current_user.id).first()
    if existing_property:
      flash(f"A property with the name {existing_property.name} already exists", category="warning")
    else:
      db.session.add(new_property)
      db.session.commit()
      flash(f"Property {new_property.name}  was created successfully",category="success")
      return redirect(url_for('landlord.property_information', property_id=new_property.unique_id))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")

  return render_template("Landlord/property-registration.html", form=form)

@landlords.route("/update-property/<int:property_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def edit_property(property_id):
  try:
    form = PropertyRegistrationForm()
    edit_property = Properties.query.filter_by(unique_id=property_id).first()
    if edit_property.property_owner != current_user.id:
      flash("You do not have permission to edit this property.", category="danger")
      return redirect(url_for('landlord.landlord_dashboard'))
    if form.validate_on_submit():
      if form.name.data != edit_property.name:
        existing_property = Properties.query.filter_by(name=form.name.data, property_owner=current_user.id).first()
        if existing_property:
          flash(f"A property with the name {existing_property.name} already exists", category="warning")
      else:
        edit_property.property_floors = form.floors.data,
        db.session.commit()
        flash(f"Property {edit_property.name}  updated successfully",category="success")
      return redirect(url_for('landlord.property_information', property_id=edit_property.unique_id))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")
  
    return render_template("Landlord/edit-property.html", form=form, property=edit_property)

  except Exception as e:
    flash(f"An error occurred: {repr(e)}", category="danger")
    db.session.rollback()
    return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/delete-property/<int:property_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def delete_property(property_id):
  try:
    landlord_property = Properties.query.filter_by(unique_id=property_id).first()
    if not landlord_property:
      flash("Property not found", category="danger")
    elif landlord_property.tenant or landlord_property.unit:
      flash(f"Cannot remove property. You have tenants or units registered, remove them first", category="danger")
      return redirect(url_for("landlord.property_information", property_id=landlord_property.unique_id))
    elif landlord_property.property_owner != current_user.id:
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
@landlord_role_required("Landlord")
def add_unit(property_id):
  form = UnitRegistrationForm()
  current_property = Properties.query.filter_by(unique_id=property_id).first()
  form.unit_type.choices = [unit_type.name for unit_type in current_property.unit_type]
  try:
    if form.validate_on_submit():
      new_unit = Unit(
        name = form.name.data,
        unit_floor = form.floor.data,
        unit_type = form.unit_type.data,
        date_added = datetime.now(),
        rent_amount = form.rent_amount.data,
        properties = current_property.id,
        landlord = current_user.id
      )
      if check_if_unit_exists(current_property.id, new_unit.name):
        return redirect(url_for('landlord.property_information',property_id=current_property.unique_id))
      if check_if_floor_exists(current_property.id, new_unit.unit_floor):
        return redirect(url_for('landlord.property_information',property_id=current_property.unique_id))
      if check_if_property_is_full(current_property.id):
        return redirect(url_for('landlord.property_information',property_id=current_property.unique_id))
      db.session.add(new_unit)
      db.session.commit()
      flash(f"Unit {new_unit.name} - {new_unit.unit_type} Added successfully",category="success")
      return redirect(url_for('landlord.upload_unit_metrics',unit_id=new_unit.unique_id))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")

    return render_template("Landlord/unit-registration.html", form=form)
  except Exception as e:
    flash(f"{repr(e)}. Try again later", category="danger")
    return redirect(url_for("landlord.property_information", property_id=current_property.unique_id))

def check_if_unit_exists(property_id, new_unit_name):
  current_property = Properties.query.get(property_id)
  unit = Unit.query.filter_by(name=new_unit_name, properties=property_id).first()
  if unit:
    flash(f"A unit with name {new_unit_name} already exists in {current_property.name}", category="warning")
    return True

def check_if_floor_exists(property_id, new_unit_floor):
  current_property = Properties.query.get(property_id)
  if new_unit_floor > current_property.property_floors or new_unit_floor < 0:
    flash(f"Floor {new_unit_floor} does not exist", category="danger")
    return True

def check_if_property_is_full(property_id):
  current_property = Properties.query.get(property_id)
  units = Unit.query.filter_by(properties=property_id).all()
  if len(units) >= current_property.rooms:
    flash(f"Maximum units allowed of this property has been reached", category="warning")
    return False

@landlords.route("/upload-unit-metrics/<int:unit_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def upload_unit_metrics(unit_id):
  # try:
  form = UnitMetricRegistrationForm()
  current_unit = Unit.query.filter_by(unique_id=unit_id).first()
  if not current_unit:
    flash("Unit not found", category="danger")
    return redirect(url_for('landlord.landlord_dashboard'))
  current_property = Properties.query.filter_by(id=current_unit.properties).first()
  if form.validate_on_submit():
    new_unit_metrics = UnitMetrics(
      living_space = form.living_room_space.data,
      balcony_space = form.balcony_room_space.data,
      bedrooms = form.bedrooms.data,
      bathrooms = form.bathrooms.data,
      unit = current_unit.id
    )
    files = request.files.getlist("unit_image")
    db.session.add(new_unit_metrics)
    if asyncio.run(upload_file(current_unit.unique_id, files)) is True:
      return redirect(url_for('landlord.property_information', property_id=current_property.unique_id))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")
    return redirect(url_for('landlord.upload_unit_metrics', unit_id=current_unit.unique_id))

  return render_template("Landlord/unit-metrics.html", form=form)
  # except Exception as e:
  #   flash(f"{repr(e)}. Try again later", category="danger")
  #   return redirect(url_for("landlord.property_information", property_id=current_property.id))

async def upload_file(unit_id, files):
  unit = Unit.query.filter_by(unique_id=unit_id).first()
  if not unit:
    flash("Unit not found", category="danger")
    return redirect(url_for('landlord.landlord_dashboard'))
  try:
    for file in files:
      unit_image = UnitImage(
        name = file.filename,
        bucket = bucket_name,
        region = region,
        unit = unit.id
      )
      s3.Object(bucket_name, file.filename).put(Body=file)
      db.session.add(unit_image)
      db.session.commit()
      flash("Unit metrics uploaded successfully", category="success")
      return True
  except NoCredentialsError:
    flash("Credentials not available", category="danger")
    return redirect(url_for('landlord.upload_unit_metrics', unit_id=unit.unique_id))
  except PartialCredentialsError:
    flash("Incomplete credentials provided", category="danger")
    return redirect(url_for('landlord.upload_unit_metrics', unit_id=unit.unique_id))
  except ClientError as e:
    flash(f"Client Error: {e.response['Error']['Message']}", category="danger")
    return redirect(url_for('landlord.upload_unit_metrics', unit_id=unit.unique_id))
  except Exception as e:
    flash(f"Error: {repr(e)}", category="danger")
    return redirect(url_for('landlord.upload_unit_metrics', unit_id=unit.unique_id))

@landlords.route("/register-unit-type/<int:property_id>", methods=["POST"])
@login_required
@landlord_role_required("Landlord")
def register_unit_type(property_id):
  try:
    form = UnitTypeForm()
    landlord_property = Properties.query.filter_by(unique_id=property_id).first()
    new_unit_type = UnitTypes(
      name = form.unit_type.data,
      properties = landlord_property.id
    )
    db.session.add(new_unit_type)
    db.session.commit()
    flash(f"{new_unit_type.name} added to {landlord_property.name}", category="success")
    return redirect(url_for('landlord.property_information', property_id=landlord_property.unique_id))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/remove-unit-type/<int:unit_type_id>")
@login_required
@landlord_role_required("Landlord")
def remove_unit_type(unit_type_id):
  try:
    unit_type = UnitTypes.query.filter_by(unique_id=unit_type_id).first()
    if not unit_type:
      flash("Unit Type not found", category="danger")
      return redirect(url_for('landlord.landlord_dashboard'))
    landlord_property = Properties.query.get(unit_type.properties)
    db.session.delete(unit_type)
    db.session.commit()
    flash(f"{unit_type.name} removed", category="success")
    return redirect(url_for('landlord.property_information', property_id=landlord_property.unique_id))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/update-property-availability/<int:property_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
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
@landlord_role_required("Landlord")
def extra_service(extra_type):
  extras = Extras.query.filter_by(title=extra_type).all()
  properties = Properties.query.filter(Properties.property_owner == current_user.id).all()
  units = Unit.query.filter(Unit.landlord == current_user.id).all()

  return render_template("Landlord/extra_services.html", extras=extras, extra_type=extra_type, properties=properties, units=units)

@landlords.route("/extra-services/<int:property_id>", methods=["POST", "GET"])
@login_required
@landlord_role_required("Landlord")
def unit_select(property_id):
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
@landlord_role_required("Landlord")
def select_extra_service(extra_id): 
  if request.get_data('data'):
    data = json.loads(request.get_data('data'))
  extra = Extras.query.filter_by(id=data.get("extra")).first()
  active_extras = ExtraService.query.filter(ExtraService.landlord == current_user.id, ExtraService.status == "Ongoing", ExtraService.extra == extra_id).all()
  if active_extras:
    extra_occupancy(extra_id)
  else:
    try:
      new_service = ExtraService(
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
@landlord_role_required("Landlord")
def extra_occupancy(extra_id):
  extra = Extras.query.get(extra_id)
  active_extras = ExtraService.query.filter_by(landlord = current_user.id, status="Ongoing", extra=extra.id).all()
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
@landlord_role_required("Landlord")
def delete_extra_service(extra_service_id):
  maintenance = ExtraService.query.get(extra_service_id)
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
@landlord_role_required("Landlord")
def complete_extra_service(extra_service_id):
  maintenance = ExtraService.query.get(extra_service_id)
  if maintenance:
    maintenance.date_closed = datetime.now()
    maintenance.status = "Closed"
    db.session.commit()
    flash(f"Maintenance #{maintenance.extra_service_id} marked as complete", category="success")
  else:
    flash("Maintenance record not found", category="danger")

  return redirect(url_for('landlord.landlord_dashboard'))
