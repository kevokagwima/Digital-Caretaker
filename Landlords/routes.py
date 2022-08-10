from flask import Blueprint, jsonify, render_template, flash, url_for, redirect, request, session, abort, json
from flask_login import login_user, login_required, fresh_login_required, logout_user, current_user
from twilio.rest import Client
from models import db, Landlord, Tenant, Unit, Properties, Extras, Verification, Transaction, Members, Bookings, Complaints, Extra_service, Invoice
from .form import *
import random, os, datetime
from datetime import date, datetime, timedelta

landlords = Blueprint("landlord", __name__)

SECRET_KEY = os.environ['Hms_secret_key']
google_maps =os.environ["Google_maps"]
account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)

today = datetime.now()

@landlords.route("/landlord_registration", methods=["POST", "GET"])
def landlord():
  form = landlord_form()
  try:
    if form.validate_on_submit():
      new_landlord = Landlord(
        first_name=form.first_name.data,
        second_name=form.second_name.data,
        last_name=form.last_name.data,
        email=form.email_address.data,
        phone=form.phone_number.data,
        username=form.username.data,
        date=datetime.now(),
        active="True",
        landlord_id=random.randint(100000, 999999),
        account_type="Landlord",
        passwords=form.password.data,
      )
      db.session.add(new_landlord)
      db.session.commit()
      #clients.messages.create(
        #to = '+254796897011',
        #from_ = '+16203191736',
        #body = f'Congratulations! {new_landlord.first_name} {new_landlord.second_name} you have successfully created your landlord account. \nLogin to your dashboard using your Landlord ID {new_landlord.landlord_id} and your password. \nDo not share your Landlord ID with anyone other than your tenants only when they register.'
      #)
      flash(f"Account created successfully", category="success")
      return redirect(url_for("landlord.Landlord_login"))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the account: {err_msg}",category="danger")
  except:
    flash(f"Something went wrong. Check your form and try again", category="danger")

  return render_template("landlord.html", form=form)

@landlords.route("/landlord_login", methods=["POST", "GET"])
def Landlord_login():
  form = landlord_login_form()
  if form.validate_on_submit():
    new_landlord = Landlord.query.filter_by(landlord_id=form.landlord_id.data).first()
    if new_landlord and new_landlord.check_password_correction(attempted_password=form.password.data):
      login_user(new_landlord, remember=True)
      flash(f"Login successfull, welcome {new_landlord.first_name}",category="success")
      next = request.args.get("next")
      return redirect(next or url_for("landlord.landlord_dashboard"))
    elif new_landlord == None:
      flash(f"No user with that Landlord ID", category="danger")
      return redirect(url_for("landlord.Landlord_login"))
    else:
      flash(f"Invalid credentials", category="danger")
      return redirect(url_for("landlord.Landlord_login"))

  return render_template("landlord_login.html", form=form)

@landlords.route("/Landlord_dashboard", methods=["POST", "GET"])
@fresh_login_required
@login_required
def landlord_dashboard():
  if current_user.account_type != "Landlord":
    abort(403)
  properties = db.session.query(Properties).filter(current_user.id == Properties.owner).all()
  tenants = db.session.query(Tenant).filter(Tenant.landlord == current_user.id).all()
  todays_time = today.strftime("%d/%m/%Y")
  expenses = 0
  properties_count = db.session.query(Properties).filter(Properties.owner == current_user.id).count()
  extras = Extras.query.all()
  active_extras = Extra_service.query.filter(Extra_service.landlord == current_user.id).all()
  units = Unit.query.filter(Unit.landlord == current_user.id, Unit.tenant != None).all()
  if units:
    for unit in units:
      unit_transactions = Transaction.query.filter_by(Unit=unit.id).all()
      if unit_transactions:
        for transaction in unit_transactions:
          if transaction.next_date < date.today():
            invoice = Invoice.query.filter_by(id=transaction.invoice).first()
            if invoice:
              pass
            else:
              new_invoice = Invoice(
                invoice_id = random.randint(100000,999999),
                tenant = unit.tenant,
                unit = unit.id,
                amount = unit.rent_amount,
                date_created = datetime.now(),
                status = "Active"
              )
              db.session.add(new_invoice)
              db.session.commit()
      else:
        invoices = Invoice.query.filter_by(unit=unit.id).all()
        if invoices:
          for invoice in invoices:
            invoice_month = invoice.date_created.strftime("%m")
            this_month = datetime.now().strftime("%m")
            if invoice_month == this_month:
              pass
        else:
          new_invoice = Invoice(
            invoice_id = random.randint(100000,999999),
            tenant = unit.tenant,
            unit = unit.id,
            amount = unit.rent_amount,
            date_created = datetime.now(),
            status = "Active"
          )
          db.session.add(new_invoice)
          db.session.commit()

  return render_template("new_dash.html",properties=properties, tenants=tenants,properties_count=properties_count, expenses=expenses, extras=extras, todays_time=todays_time, units=units, active_extras=active_extras)

@landlords.route("/approve-verification/<int:verification_id>")
@fresh_login_required
@login_required
def approve_verification(verification_id):
  if current_user.account_type != "Landlord":
    abort(403)
  verification = Verification.query.get(verification_id)
  tenant = Tenant.query.filter_by(id=verification.tenant).first()
  unit = Unit.query.filter_by(tenant=tenant.id).first()
  transactions = db.session.query(Transaction).filter(Transaction.tenant == tenant.id).all()
  invoice = Invoice.query.filter(Invoice.unit == unit.id, Invoice.status == "Active").first()
  if verification and invoice:
    verification.status = 'approved'
    new_transaction = Transaction (
      tenant = tenant.id,
      landlord = current_user.id,
      Property = tenant.properties,
      Unit = unit.id,
      date = datetime.now(),
      time = datetime.now(),
      next_date = datetime.now() + timedelta(days=30),
      transaction_id = random.randint(100000, 999999),
      invoice = invoice.id,
      origin = "Mpesa"
    )
    if transactions and transactions[-1].next_date > datetime.now():
      flash(f"The tenant has already paid this month's rent", category="danger")
      verification.status = "denied"
      db.session.commit()
    else:
      db.session.add(new_transaction)
      invoice.date_closed = datetime.now()
      invoice.status = "Cleared"
      db.session.commit()
      #clients.messages.create(
        #to = '+254796897011',
        #from_ = '+16203191736',
        #body = f'Confirmed! rental payment of amount {unit.rent_amount} paid successfully on {new_transaction.date}. Next charge will be on {new_transaction.next_date}'
      #)
      flash(f"Rent payment approved", category="success")
      return redirect(url_for('landlord.landlord_dashboard'))
  else:
    verification.status = 'failed'
    db.session.commit()
    flash(f"Failed to approve the mpesa transaction.", category=
    "danger")
  return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/deny-verification/<int:verification_id>")
@fresh_login_required
@login_required
def deny_verification(verification_id):
  if current_user.account_type != "Landlord":
    abort(403)
  verification = Verification.query.get(verification_id)
  if verification.status == "denied":
    flash(f"Rent payment already denied", category="danger")
  else:
    verification.status = 'denied'
    db.session.commit()
    flash(f"Rent payment denied", category="success")

  return redirect(url_for('landlord.landlord_dashboard'))

@landlords.route("/property_information/<int:property_id>", methods=["POST","GET"])
@fresh_login_required
@login_required
def property_information(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    properties = db.session.query(Properties).filter(current_user.id == Properties.owner).all()
    propertiez = Properties.query.filter_by(id=property_id).first()
    users = Members.query.all()
    landlord_user = Landlord.query.all()
    tenant_user = Tenant.query.all()
    today_time = today.strftime("%d/%m/%Y")
    session["property"] = propertiez
    if propertiez.owner != current_user.id:
      flash(f"Unknown Property", category="info")
      return redirect(url_for("landlord.landlord_dashboard"))
    tenants = db.session.query(Tenant).filter(Tenant.properties == propertiez.id).all()
    units = db.session.query(Unit).filter(Unit.Property == propertiez.id).all()
    tenants_count = db.session.query(Tenant).filter(Tenant.properties == propertiez.id).count()
    unit_count = db.session.query(Unit).filter(Unit.Property == propertiez.id).count()
    reservations = Bookings.query.filter_by(property=propertiez.id).all()
    active_reservations = []
    for reservation in reservations:
      if reservation.expiry_date < datetime.now() and reservation.status == "Active":
        active_reservations.append(reservation)
        unit = Unit.query.filter_by(id=reservation.unit).first()
        unit.reserved = "False"
        reservation.status = "Expired"
        db.session.commit()
    if len(active_reservations) == 1:
      flash(f"You have one reservation that has expired", category="warning")
    elif len(active_reservations) > 1:
      active_reservations_count = len(active_reservations)
      flash(f"You have {active_reservations_count} reservations that have Expired", category="warning")
    unitz = Unit.query.filter(Unit.landlord == current_user.id, Unit.tenant != None).all()
    if unitz:
      for unit in unitz:
        unit_transactions = Transaction.query.filter_by(Unit=unit.id).all()
        if unit_transactions:
          for transaction in unit_transactions:
            if transaction.next_date < date.today():
              invoice = Invoice.query.filter_by(id=transaction.invoice).first()
              if invoice:
                pass
              else:
                new_invoice = Invoice(
                  invoice_id = random.randint(100000,999999),
                  tenant = unit.tenant,
                  unit = unit.id,
                  amount = unit.rent_amount,
                  date_created = datetime.now(),
                  status = "Active"
                )
                db.session.add(new_invoice)
                db.session.commit()
        else:
          invoices = Invoice.query.filter_by(unit=unit.id).all()
          if invoices:
            for invoice in invoices:
              invoice_month = invoice.date_created.strftime("%m")
              this_month = datetime.now().strftime("%m")
              if invoice_month == this_month:
                pass
          else:
            new_invoice = Invoice(
              invoice_id = random.randint(100000,999999),
              tenant = unit.tenant,
              unit = unit.id,
              amount = unit.rent_amount,
              date_created = datetime.now(),
              status = "Active"
            )
            db.session.add(new_invoice)
            db.session.commit()
  except:
    flash(f"Cannot retrieve property information at the moment. Try again later", category="warning")
    return redirect(url_for("landlord.landlord_dashboard"))

  return render_template("property_dashboard.html",propertiez=propertiez,properties=properties,tenants=tenants,units=units,tenants_count=tenants_count,unit_count=unit_count, today_time=today_time,users=users, landlord_user=landlord_user, tenant_user=tenant_user)

@landlords.route("/tenant_details/<int:tenant_id>", methods=["GET", "POST"])
@fresh_login_required
@login_required
def tenant_details(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  today_time = today.strftime("%d/%m/%Y")
  try:
    tenant = Tenant.query.get(tenant_id)
    if tenant.landlord != current_user.id:
      flash(f"Unknown Tenant ID", category="info")
      return redirect(url_for("landlord.landlord_dashboard"))
    elif tenant.active == "False":
      flash(f"Cannot view tenant details. Tenant is not active", category="danger")
      this_property = session["property"]
      return redirect(url_for("landlord.property_information", property_id=this_property.id))
    complaints = Complaints.query.filter_by(tenant=tenant.id).all()
    unit = Unit.query.filter_by(tenant=tenant.id).first()
    unitz = Unit.query.filter(Unit.landlord == current_user.id, Unit.tenant != None).all()
    if unitz:
      for unit in unitz:
        unit_transactions = Transaction.query.filter_by(Unit=unit.id).all()
        if unit_transactions:
          for transaction in unit_transactions:
            if transaction.next_date < date.today():
              invoice = Invoice.query.filter_by(id=transaction.invoice).first()
              if invoice:
                pass
              else:
                new_invoice = Invoice(
                  invoice_id = random.randint(100000,999999),
                  tenant = unit.tenant,
                  unit = unit.id,
                  amount = unit.rent_amount,
                  date_created = datetime.now(),
                  status = "Active"
                )
                db.session.add(new_invoice)
                db.session.commit()
        else:
          invoices = Invoice.query.filter_by(unit=unit.id).all()
          if invoices:
            for invoice in invoices:
              invoice_month = invoice.date_created.strftime("%m")
              this_month = datetime.now().strftime("%m")
              if invoice_month == this_month:
                pass
          else:
            new_invoice = Invoice(
              invoice_id = random.randint(100000,999999),
              tenant = unit.tenant,
              unit = unit.id,
              amount = unit.rent_amount,
              date_created = datetime.now(),
              status = "Active"
            )
            db.session.add(new_invoice)
            db.session.commit()
  except:
    flash(f"Something went wrong. Try again", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

  return render_template("tenant_details.html",tenant=tenant,complaints=complaints,unit=unit, today_time=today_time)

@landlords.route("/Assign_unit", methods=["POST", "GET"])
@fresh_login_required
@login_required
def assign_tenant():
  if current_user.account_type != "Landlord":
    abort(403)
  tenant_id = request.form.get("tenant_id")
  unit_id = request.form.get("unit_id")
  previous_url = request.referrer
  this_property = session["property"]
  try:
    tenant = Tenant.query.filter_by(tenant_id=tenant_id).first()
    unit = Unit.query.filter_by(unit_id=unit_id).first()
    if tenant.landlord != current_user.id:
      flash(f"Unknown Tenant ID. Try again", category="info")
      return redirect(previous_url)
    elif tenant.properties == None:
      flash(f"No property is assigned to the tenant", category="info")
      return redirect(previous_url)
    elif tenant.properties != this_property.id:
      flash(f"Cannot assign a unit to a tenant from a different property", category="info")
      return redirect(previous_url)
    elif unit.landlord != current_user.id:
      flash(f"Unknown Unit ID. Try again", category="info")
      return redirect(previous_url)
    elif unit.Property != this_property.id:
      flash(f"Cannot assign a tenant a unit from a different property", category="info")
      return redirect(previous_url)
    elif tenant and unit:
      if tenant.unit or unit.tenant or unit.reserved == "True":
        flash(f"Could not assign unit. Unit already occupied or reserved or tenant has a unit. Try again",category="danger")
        return redirect(url_for("landlord.property_information", property_id=this_property.id))
      elif tenant.active == "False":
          flash(f"Cannot assign unit, tenant is not active", category="danger")
          return redirect(previous_url)
      else:
        unit.tenant = tenant.id
        db.session.commit()
        flash(f"Unit {unit.name} - {unit.Type} assigned to {tenant.first_name} {tenant.second_name} successfully",category="success")
        return redirect(url_for("landlord.property_information", property_id=this_property.id))
  except:
    flash(f"Invalid Tenant ID or Unit ID. Try again",category="danger")
    return redirect(previous_url)

  return render_template("property_dashboard.html")

@landlords.route("/assign-tenant/<int:tenant_id>", methods=["POST", "GET"])
@fresh_login_required
@login_required
def assign_unit_now(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  unit_id = request.form.get("unit-assign")
  previous_url = request.referrer
  try:
    tenant = Tenant.query.get(tenant_id)
    unit = Unit.query.get(unit_id)
    if unit.reserved == "True":
      flash(f"Cannot assign unit, Unit is reserved", category="danger")
      return redirect(previous_url)
    elif unit.tenant:
      flash(f"Cannot assign unit, Unit is occupied", category="danger")
      return redirect(previous_url)
    elif tenant.properties == None:
      flash(f"No property is assigned to the tenant", category="info")
      return redirect(previous_url)
    elif tenant and unit:
      unit.tenant = tenant.id
      db.session.commit()
      flash(f"Unit {unit.name} - {unit.Type} assigned to {tenant.first_name} {tenant.second_name} successfully", category="success")
      return redirect(url_for('landlord.tenant_details', tenant_id=tenant.id))
    else:
      flash(f"Invalid Unit", category="danger")
      return redirect(previous_url)
  except:
    flash(f"Something went wrong", category="danger")
    return redirect(previous_url)

@landlords.route("/revoke_tenant,", methods=["POST", "GET"])
@fresh_login_required
@login_required
def remove_tenant():
  if current_user.account_type != "Landlord":
    abort(403)
  tenant_id = (request.form.get("tenant_id"))
  previous_url = request.referrer
  this_property = session["property"]
  try:
    tenant = Tenant.query.filter_by(tenant_id=tenant_id).first()
    if tenant.landlord != current_user.id:
      flash(f"Unknown Tenant ID", category="info")
      return redirect(previous_url)
    elif tenant.properties != this_property.id:
      flash(f"Cannot revoke access of a tenant from a different property", category="info")
      return redirect(previous_url)
    elif tenant.active == "False":
      flash(f"{tenant.first_name} {tenant.second_name}'s Account is already revoked",category="danger")
      return redirect(previous_url)
    elif tenant:
      if tenant.unit:
        unit = db.session.query(Unit).filter(tenant.id == Unit.tenant).first()
        unit.tenant = None
      elif tenant.complaint:
        complaints = db.session.query(Complaints).filter(tenant.id == Complaints.tenant).all()
        for complaint in complaints:
          db.session.delete(complaint)
        db.session.commit()
      elif tenant.transact:
        transactions = db.session.query(Transaction).filter(tenant.id == Transaction.tenant).all()
        db.session.delete(transactions)
        db.session.commit()
      tenant.active = "False"
      tenant.landlord = None
      tenant.properties = None
      db.session.commit()
      flash(f"{tenant.first_name} {tenant.second_name}'s Account Revoked successfully",category="success")
      return redirect(previous_url)
  except:
    flash(f"Invalid Tenant ID. Try again", category="danger")
    return redirect(previous_url)
  
  return render_template("property_dashboard.html")

@landlords.route("/revoke_tenant/<int:tenant_id>", methods=["POST", "GET"])
@fresh_login_required
@login_required
def remove_tenant_now(tenant_id):
  if current_user.account_type != "Landlord":
    abort(403)
  previous_url = request.referrer
  this_property = session["property"]
  tenant = Tenant.query.get(tenant_id)
  if tenant.landlord != current_user.id:
    flash(f"Unknown Tenant ID", category="info")
    return redirect(previous_url)
  elif tenant.active == "False":
    flash(f"{tenant.first_name} {tenant.second_name}'s Account is already revoked",category="danger")
    return redirect(previous_url)
  elif tenant:
    if tenant.unit:
      unit = db.session.query(Unit).filter(tenant.id == Unit.tenant).first()
      unit.tenant = None
    elif tenant.complaint:
      complaints = db.session.query(Complaints).filter(tenant.id == Complaints.tenant).all()
      for complaint in complaints:
        db.session.delete(complaint)
      db.session.commit()
    elif tenant.transact:
      transactions = db.session.query(Transaction).filter(tenant.id == Transaction.tenant).all()
      db.session.delete(transactions)
      db.session.commit()
    tenant.active = "False"
    tenant.landlord = None
    tenant.properties = None
    db.session.commit()
    flash(f"{tenant.first_name} {tenant.second_name}'s Account Revoked successfully. Tenant no longer part of your tenant list.",category="success")
    return redirect(url_for("landlord.property_information", property_id=this_property.id))

  return render_template("property_dashboard.html")

@landlords.route("/property-registration", methods=["POST", "GET"])
@fresh_login_required
@login_required
def property():
  if current_user.account_type != "Landlord":
    abort(403)
  if session.get("property"):
    this_property = session["property"]
  try:
    new_property = Properties(
      name=request.form.get("property_name"),
      address=request.form.get("property-address"),
      address2 =request.form.get("property-address2"),
      floors=request.form.get("property-floors"),
      rooms=request.form.get("property-units"),
      Type=request.form.get("property-type"),
      property_id=random.randint(100000, 999999),
      date=datetime.now(),
      owner=current_user.id,
      status=request.form.get("availability")
    )
    if new_property.owner != current_user.id:
      flash(f"The landlord ID you entered does not match your landlord ID", category="info")
    for prop in current_user.Property:
      if prop.name == new_property.name:
        flash(f"A property with the name {prop.name} already exists", category="danger")
        return redirect(url_for("landlord.property_information", property_id=this_property.id))
    else:
      db.session.add(new_property)
      db.session.commit()
      flash(f"Property {new_property.name}  was created successfully",category="success")
      return redirect(url_for("landlord.property_information", property_id=new_property.id))
  except:
    flash(f"Something went wrong. Try again later", category="danger")
    return redirect(url_for("landlord.property_information", property_id=this_property.id))

@landlords.route("/delete_property/<int:property_id>", methods=["POST", "GET"])
@fresh_login_required
@login_required
def delete_property(property_id):
  if current_user.account_type != "Landlord":
    abort(403)
  try:
    property = Properties.query.get(property_id)
    if property.tenants or property.unit:
      flash(f"Cannot remove {property.name}.  Some tenants or units are still linked",category="danger")
      return redirect(url_for("landlord.property_information", property_id=property.id))
    elif property.owner != current_user.id:
      flash(f"No property with the name {property.name}",category="danger",)
      return redirect(url_for("landlord.landlord_dashboard"))
    elif property:
      db.session.delete(property)
      db.session.commit()
      flash(f"Property {property.name} has been decommissioned successfully",category="success",)
      return redirect(url_for("landlord.landlord_dashboard"))
    else:
      flash(f"Property {property.name} could not be deleted. Try again",category="danger")
      return redirect(url_for("landlord.property_information", property_id=property.id))
  except:
    flash(f"An error occurred", category="danger")
    return redirect(url_for("landlord.landlord_dashboard"))

@landlords.route("/Landlord_portal/Property_registration/Unit_registration", methods=["POST", "GET"])
@fresh_login_required
@login_required
def unit():
  if current_user.account_type != "Landlord":
    abort(403)
  this_property = session["property"]
  try:
    new_unit = Unit(
      name=request.form.get("unit-name"),
      floor=request.form.get("unit-floor"),
      Type=request.form.get("unit-type"),
      date=datetime.now(),
      unit_id=random.randint(100000, 999999),
      rent_amount=request.form.get("unit-rent"),
      living_space=request.form.get("living-space"),
      balcony_space=request.form.get("veranda"),
      bedrooms = request.form.get("no-of-bedrooms"),
      bathrooms = request.form.get("no-of-bathrooms"),
      air_conditioning = request.form.get("air-conditioning"),
      amenities = request.form.get("furniture"),
      reserved="False",
      Property=Properties.query.filter_by(property_id=request.form.get("property-id")).first().id,
      landlord=Landlord.query.filter_by(id=current_user.id).first().id
    )
    all_units = Unit.query.filter_by(Property=this_property.id).all()
    for unit in all_units:
      unit_exists = db.session.query(Unit).filter(new_unit.name == unit.name).first()
      if unit_exists:
        flash(f"A unit with name {new_unit.name} already exists in {this_property.name}", category="danger")
        return redirect(url_for("landlord.property_information", property_id=this_property.id))
    all_units_count = Unit.query.filter_by(Property=this_property.id).count()
    if all_units_count == this_property.rooms:
      flash(f"Maximum units allowed of this property has been reached", category="warning")
      return redirect(url_for("landlord.property_information", property_id=this_property.id))
    if this_property.Type == "Office":
      new_unit.bedrooms = 0
      new_unit.bathrooms = 0
      db.session.commit()
    if new_unit.Property != this_property.id:
      flash(f"Invalid Property ID", category="danger")
      return redirect(url_for("landlord.property_information", property_id=this_property.id))
    db.session.add(new_unit)
    db.session.commit()
    flash(f"Unit {new_unit.name} - {new_unit.Type} Added successfully",category="success")
    return redirect(url_for("landlord.property_information", property_id=this_property.id))
  except:
    flash(f"Something went wrong. Try again later", category="danger")
    return redirect(url_for("landlord.property_information", property_id=this_property.id))

@landlords.route("/update-property-availability/<int:property_id>", methods=["POST", "GET"])
@fresh_login_required
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
@fresh_login_required
@login_required
def extra_service(extra_type):
  if current_user.account_type != "Landlord":
    abort(403)
  extras = Extras.query.filter_by(title=extra_type).all()
  properties = Properties.query.filter(Properties.owner == current_user.id).all()
  units = Unit.query.filter(Unit.landlord == current_user.id).all()

  return render_template("extra_services.html", extras=extras, extra_type=extra_type, properties=properties, units=units)

@landlords.route("/extra-services/<int:property_id>", methods=["POST", "GET"])
@fresh_login_required
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
@fresh_login_required
@login_required
def select_extra_service(extra_id):
  if current_user.account_type != "Landlord":
    abort(403)
  data = json.loads(request.get_data('data'))
  Property = Properties.query.filter_by(id=data.get("property")).first()
  extra = Extras.query.filter_by(id=data.get("extra")).first()
  active_extras = Extra_service.query.filter(Extra_service.landlord == current_user.id, Extra_service.status == "Ongoing", Extra_service.extra == extra.id).all()
  if active_extras:
    extra_occupancy(extra.id)
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
@fresh_login_required
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

@landlords.route("/logout_landlord")
@login_required
def landlord_logout():
  if current_user.account_type != "Landlord":
    abort(403)
  logout_user()
  flash(f"Logged out successfully!", category="success")
  return redirect(url_for("landlord.Landlord_login"))
