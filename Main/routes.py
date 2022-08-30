from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_user, login_required, fresh_login_required, logout_user, current_user
from models import Members, db, Landlord,Tenant, Properties, Unit, Bookings
from sqlalchemy import or_
from .form import *
from modules import send_sms, send_email
import random
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

main = Blueprint("main", __name__)

@main.route("/registration", methods=["POST", "GET"])
def signup():
  form = user_registration()
  try:
    if form.validate_on_submit():
      member = Members(
        first_name=form.first_name.data,
        second_name=form.second_name.data,
        last_name=form.last_name.data,
        email=form.email_address.data,
        phone=form.phone_number.data,
        date=datetime.now(),
        account_type="member",
        username=form.username.data,
        passwords=form.password.data,
      )
      db.session.add(member)
      db.session.commit()
      message = {
        'receiver': member.email,
        'subject': 'Account Created Successfully',
        'body': f'Congratulations! {member.first_name} {member.second_name} you have successfully created your account. \nLogin using your username {member.username} and password'
      }
      # send_sms(message)
      send_email(**message)
      flash(f"User registered successfully", category="success")
      return redirect(url_for("main.signin"))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the user: {err_msg}", category="danger")
  except:
    flash(f"An error occured when submitting the form. Check your inputs and try again", category="danger")

  return render_template("signup.html", form=form)

@main.route("/signin", methods=["POST", "GET"])
def signin():
  form = login()
  if form.validate_on_submit():
    member = (
      Members.query.filter_by(username=form.username.data).first() or Landlord.query.filter_by(username=form.username.data).first() or Tenant.query.filter_by(username=form.username.data).first()
    )
    if member and member.check_password_correction(attempted_password=form.password.data):
      login_user(member, remember=True)
      flash(f"Login successfull, welcome {member.username}",category="success",)
      next = request.args.get("next")
      return redirect(next or url_for("main.index"))
    elif member == None:
      flash(f"No user with that username", category="danger")
    else:
      flash(f"Invalid login credentials", category="danger")

  return render_template("signin.html", form=form)

@main.route("/")
@main.route("/home")
def index():
  properties = Properties.query.all()
  if properties:
    property_choice = random.choice(properties)
    units = Unit.query.all()
    tenants = Tenant.query.all()
    landlords = Landlord.query.all()
    
    return render_template("index.html", properties=properties,property_choice=property_choice, units=units, tenants=tenants, landlords=landlords)
  
  return render_template("index.html")

@main.route("/about_us")
def about_us():
  return render_template("about.html")

@main.route("/services")
def services():
  return render_template("services.html")

@main.route("/contact_us")
def contact_us():
  return render_template("contact.html")

@main.route("/properties")
def properties():
  properties = Properties.query.all()
  units = Unit.query.all()
  today_time = datetime.now().strftime("%d/%m/%Y")

  return render_template("properties.html", properties=properties, units=units, today_time=today_time)

@main.route("/search-properties", methods=["POST", "GET"])
def search_property():
  search_text = request.form.get("search")
  search = search_text.title()
  propertiez = Properties.query.filter(or_(Properties.Type.like(search), Properties.address.like(search), Properties.address2.like(search))).all()
  today_time = datetime.now().strftime("%d/%m/%Y")
  if propertiez:
    for prop in propertiez:
      units = Unit.query.filter_by(Property=prop.id, tenant=None, reserved="False").all()
    if len(propertiez) > 0:
      flash(f"Search complete. Found {len(units)} results", category="success")
    elif len(propertiez) == 1:
      flash(f"Search complete. Found {len(units)} result", category="success")
    else:
      flash(f"Search complete. could not find what you're looking for. Now showing all available units", category="danger")
      return redirect(url_for('main.properties'))
  else:
    units = Unit.query.filter(or_(Unit.Type.like(search), Unit.name.like(search), Unit.bathrooms.like(search), Unit.bedrooms.like(search), Unit.rent_amount.like(search)), Unit.tenant == None, Unit.reserved == "False").all()
    properties = Properties.query.all()
    if len(units) > 0:
      flash(f"Search complete. Found {len(units)} results", category="success")
    elif len(units) == 1:
      flash(f"Search complete. Found {len(units)} result", category="success")
    else:
      flash(f"Search complete. could not find what you're looking for. Now showing all available units", category="danger")
      return redirect(url_for('main.properties'))

    return render_template("properties.html", properties=properties, units=units, today_time=today_time)

  return render_template("properties.html", units=units, today_time=today_time, propertiez=propertiez)

@main.route("/unit_details/<int:unit_id>", methods=["GET"])
def unit_details(unit_id):
  try:
    unit = Unit.query.get(unit_id)
    units = Unit.query.all()
    properties = Properties.query.all()
    today_time = datetime.now().strftime("%d/%m/%Y")
    if unit:
      property = Properties.query.filter_by(id = unit.Property).first()
      landlord = Landlord.query.get(property.owner)
      return render_template("property_details.html", unit=unit, landlord=landlord, property=property, units=units, properties=properties, today_time=today_time)
    else:
      flash(f"Property does not exist", category="danger")
      return redirect(url_for("main.properties"))
  except:
    flash(f"Could not find what you're looking for", category="warning")

  return redirect(url_for('main.properties'))

@main.route("/bookings/<int:unit_id>", methods=["POST", "GET"])
@fresh_login_required
@login_required
def book(unit_id):
  unit = Unit.query.get(unit_id)
  property = Properties.query.filter_by(id=unit.Property).first()
  booking = Bookings.query.filter_by(user=current_user.id, status="Active").count() or Bookings.query.filter_by(landlord_user=current_user.id, status="Active").count() or Bookings.query.filter_by(tenant_user=current_user.id, status="Active").count()
  try:
    if unit.tenant:
      flash(f"Unit is already occupied", category="danger")
    elif unit.reserved == "True":
      flash(f"Unit is already reserved. It will be available after 24 hrs", category="danger")
      return redirect(url_for("main.unit_details", unit_id=unit.id))
    elif booking == 4:
      flash(f"You have reached your reservation limit of (4). To reserve more units wait for your current reservations to expire", category="info")
      return redirect(url_for("main.unit_details", unit_id=unit.id))
    else:
      new_booking = Bookings(
        booking_id=random.randint(100000, 999999),
        date=datetime.now(),expiry_date=datetime.now() + timedelta(days=1),
        property=Properties.query.filter_by(id=property.id).first().id,
        unit=Unit.query.filter_by(id=unit.id).first().id,
        status="Active"
      )
      db.session.add(new_booking)
      unit.reserved = "True"
      db.session.commit()
      if current_user.account_type == "Landlord":
        new_booking.landlord_user = current_user.id
        db.session.commit()
      elif current_user.account_type == "Tenant":
        new_booking.tenant_user = current_user.id
        db.session.commit()
      elif current_user.account_type == "member":
        new_booking.user = current_user.id
        db.session.commit()
      flash(f"Reservation made successfully", category="success")
      return redirect(url_for("main.reservations"))
  except:
    flash(f"An error occurred. Try again", category="danger")
    return redirect(url_for("main.unit_details", unit_id=unit.id))

@main.route("/my_reservations")
@fresh_login_required
@login_required
def reservations():
  booking = Bookings.query.filter_by(user=current_user.id).all() or Bookings.query.filter_by(landlord_user=current_user.id).all() or Bookings.query.filter_by(tenant_user=current_user.id).all()
  properties = Properties.query.all()
  units = Unit.query.all()
  expired_reservations = []
  if booking:
    for overbook in booking:
      reserved_property = Properties.query.filter_by(id=overbook.property).first()
      if overbook.expiry_date < datetime.now()and overbook.status == "Active":
        expired_reservations.append(overbook)
        unit = Unit.query.filter_by(id=overbook.unit).first()
        unit.reserved = "False"
        overbook.status = "Expired"
        db.session.commit()
    loc = Nominatim(user_agent="GetLoc")
    location_text = f"{reserved_property.address}, {reserved_property.address2}"
    getLoc = loc.geocode(location_text)
    print("Latitude = ", getLoc.latitude, "\n")
    print("Longitude = ", getLoc.longitude)

    if len(expired_reservations) == 1:
      flash(f"One of your reservations has expired", category="info")
    elif len(expired_reservations) > 1:
      all_expired = len(expired_reservations)
      flash(f"{all_expired} of your reservations have expired", category="info")
  else:
    return render_template("reservations.html")
  
  return render_template("reservations.html", booking=booking, units=units, properties=properties)

@main.route("/delete-reservations/<int:reservation_id>")
@fresh_login_required
@login_required
def delete_reservation(reservation_id):
  booking = Bookings.query.filter_by(booking_id=reservation_id).first()
  unit = Unit.query.filter_by(id=booking.unit).first()
  unit.reserved = "False"
  db.session.delete(booking)
  db.session.commit()
  flash(f"Reservation deleted successfully", category="success")
  return redirect(url_for('main.reservations'))

@main.route("/logout")
@login_required
def logout():
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for("main.signin"))
