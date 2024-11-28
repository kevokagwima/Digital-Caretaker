from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, fresh_login_required, current_user
from Models.base_model import db
from Models.bookings import Bookings
from Models.property import Properties
from Models.unit import Unit
from Models.users import Tenant, Landlord

from sqlalchemy import or_
from .form import *
import random
from datetime import datetime, timedelta

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/home")
def index():
  booking = Bookings.query.all()
  properties = Properties.query.all()
  if properties:
    property_choice = random.choice(properties)
    units = Unit.query.all()
    tenants = Tenant.query.all()
    landlords = Landlord.query.all()
    
    return render_template("Main/index.html", properties=properties,property_choice=property_choice, units=units, tenants=tenants, landlords=landlords, booking=booking)
  
  return render_template("Main/index.html")

@main.route("/about_us")
def about_us():
  return render_template("Main/about.html")

@main.route("/services")
def services():
  return render_template("Main/services.html")

@main.route("/contact_us")
def contact_us():
  return render_template("Main/contact.html")

@main.route("/properties")
def properties():
  booking = Bookings.query.all()
  properties = Properties.query.all()
  page = request.args.get('page', 1, type=int)
  query = Unit.query.filter_by(tenant=None).order_by(Unit.id)
  units = query.paginate(page=page, per_page=8, error_out=False)
  next_url = url_for('main.properties', page=units.next_num) if units.has_next else None
  prev_url = url_for('main.properties', page=units.prev_num) if units.has_prev else None
  today_time = datetime.now().strftime("%d/%m/%Y")

  return render_template("Main/properties.html", properties=properties, units=units.items, today_time=today_time, booking=booking, next_url=next_url, prev_url=prev_url, next_page_number = units.next_num, prev_page_number = units.prev_num)

@main.route("/search", methods=["POST", "GET"])
def search_property():
  search_text = request.form.get("search")
  search = search_text.title()
  propertiez = Properties.query.filter(or_(Properties.Type.like(search), Properties.address.like(search), Properties.address2.like(search))).all()
  today_time = datetime.now().strftime("%d/%m/%Y")
  if propertiez:
    for prop in propertiez:
      query = Unit.query.filter_by(Property=prop.id, tenant=None).order_by(Unit.id)
      units = query.paginate(page=1, per_page=8, error_out=False)
      next_url = url_for('main.properties', page=units.next_num) if units.has_next else None
      prev_url = url_for('main.properties', page=units.prev_num) if units.has_prev else None
    if len(propertiez) > 0:
      flash(f"Search complete", category="success")
    else:
      flash(f"Search complete. could not find what you're looking for. Now showing all available units", category="danger")
      return redirect(url_for('main.properties'))
  else:
    query = Unit.query.filter(or_(Unit.Type.like(search), Unit.name.like(search), Unit.bathrooms.like(search), Unit.bedrooms.like(search), Unit.rent_amount.like(search)), Unit.tenant == None).order_by(Unit.id)
    properties = Properties.query.all()
    units = query.paginate(page=1, per_page=8, error_out=False)
    next_url = url_for('main.properties', page=units.next_num) if units.has_next else None
    prev_url = url_for('main.properties', page=units.prev_num) if units.has_prev else None
    if units.items:
      flash(f"Search complete.", category="success")
    else:
      flash(f"Search complete. could not find what you're looking for. Now showing all available units", category="danger")
      return redirect(url_for('main.properties'))

    return render_template("Main/properties.html", properties=properties, units=units.items, today_time=today_time, next_page_number = units.next_num, prev_page_number = units.prev_num, next_url=next_url, prev_url=prev_url)

  return render_template("Main/properties.html", units=units, today_time=today_time, propertiez=propertiez, next_page_number = units.next_num, prev_page_number = units.prev_num, next_url=next_url, prev_url=prev_url)

@main.route("/unit_details/<int:unit_id>", methods=["GET"])
def unit_details(unit_id):
  try:
    booking = Bookings.query.all()
    unit = Unit.query.get(unit_id)
    units = Unit.query.all()
    properties = Properties.query.all()
    today_time = datetime.now().strftime("%d/%m/%Y")
    if unit:
      property = Properties.query.filter_by(id = unit.Property).first()
      landlord = Landlord.query.get(property.owner)
      return render_template("Main/property_details.html", unit=unit, landlord=landlord, property=property, units=units, properties=properties, today_time=today_time, booking=booking)
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
  booking = Bookings.query.filter_by(user=current_user.email, status="Active").count()
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
        property_id=Properties.query.filter_by(id=property.id).first().id,
        unit=Unit.query.filter_by(id=unit.id).first().id,
        user = current_user.email,
        status="Active"
      )
      db.session.add(new_booking)
      unit.reserved = "True"
      db.session.commit()
      flash(f"Reservation made successfully", category="success")
      return redirect(url_for("main.reservations"))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("main.unit_details", unit_id=unit.id))

@main.route("/unit-enquiry/<int:unit_id>", methods=["POST", "GET"])
@fresh_login_required
@login_required
def unit_enquiry(unit_id):
  pass

@main.route("/my_reservations")
@fresh_login_required
@login_required
def reservations():
  booking = Bookings.query.filter_by(user=current_user.email, status="Active").all()
  properties = Properties.query.all()
  units = Unit.query.all()
  expired_reservations = []
  if booking:
    for overbook in booking:
      if overbook.user == current_user.id:
        reserved_property = Properties.query.filter_by(id=overbook.property_id).first()
      if overbook.expiry_date < datetime.now()and overbook.status == "Active":
        expired_reservations.append(overbook)
        unit = Unit.query.filter_by(id=overbook.unit).first()
        unit.reserved = "False"
        overbook.status = "Expired"
        db.session.commit()
    if len(expired_reservations) == 1:
      flash(f"One of your reservations has expired", category="info")
    elif len(expired_reservations) > 1:
      all_expired = len(expired_reservations)
      flash(f"{all_expired} of your reservations have expired", category="info")
  else:
    return render_template("Main/reservations.html")
  
  return render_template("Main/reservations.html", booking=booking, units=units, properties=properties)

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
