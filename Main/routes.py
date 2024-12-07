from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from Models.base_model import db
from Models.bookings import Bookings
from Models.property import Properties, PropertyTypes
from Models.unit import Unit
from Models.users import Tenant, Landlord
from .form import UnitEnquiryForm

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
  query = Unit.query.filter_by(tenant=None, is_reserved=False).order_by(Unit.id)
  units = query.paginate(page=page, per_page=8, error_out=False)
  next_url = url_for('main.properties', page=units.next_num) if units.has_next else None
  prev_url = url_for('main.properties', page=units.prev_num) if units.has_prev else None
  today_time = datetime.now().strftime("%d/%m/%Y")

  return render_template("Main/properties.html", properties=properties, units=units.items, today_time=today_time, booking=booking, next_url=next_url, prev_url=prev_url, next_page_number = units.next_num, prev_page_number = units.prev_num)

@main.route("/search", methods=["POST", "GET"])
def search_property():
  search_text = request.form.get("search")
  search = search_text.title()
  propertiez = Properties.query.filter(or_(Properties.property_type.like(search), Properties.county.like(search), Properties.city.like(search))).all()
  today_time = datetime.now().strftime("%d/%m/%Y")
  if propertiez:
    for prop in propertiez:
      query = Unit.query.filter_by(properties=prop.id, tenant=None, is_reserved=False).order_by(Unit.id)
      units = query.paginate(page=1, per_page=8, error_out=False)
      next_url = url_for('main.properties', page=units.next_num) if units.has_next else None
      prev_url = url_for('main.properties', page=units.prev_num) if units.has_prev else None
    if len(propertiez) > 0:
      flash(f"Search complete", category="success")
    else:
      flash(f"Search complete. could not find what you're looking for. Now showing all available units", category="danger")
      return redirect(url_for('main.properties'))
  else:
    query = Unit.query.filter(or_(Unit.unit_type.like(search), Unit.name.like(search), Unit.rent_amount.like(search)), Unit.tenant == None, Unit.is_reserved == False).order_by(Unit.id)
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

@main.route("/property-details/<int:unit_id>", methods=["GET"])
def unit_details(unit_id):
  try:
    unit = Unit.query.filter_by(unique_id=unit_id).first()
    if not unit:
      flash(f"Property does not exist", category="danger")
      return redirect(url_for("main.properties"))
    form = UnitEnquiryForm()
    booking = Bookings.query.all()
    current_property = Properties.query.filter_by().first()
    property_types = PropertyTypes.query.all()
    today_time = datetime.now().strftime("%d/%m/%Y")
    unit_property = Properties.query.filter_by(id=unit.properties).first()
    landlord = Landlord.query.get(unit_property.property_owner)

    return render_template("Main/property_details.html", unit=unit, landlord=landlord, property=unit_property, properties=current_property, property_types=property_types, today_time=today_time, booking=booking, form=form)
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('main.properties'))

@main.route("/reserve-unit/<int:unit_id>", methods=["POST", "GET"])
@login_required
def reserve_unit(unit_id):
  try:
    unit = Unit.query.filter_by(unique_id=unit_id).first()
    if not unit:
      flash("Unit not found", category="danger")
      return redirect(url_for('main.properties'))
    unit_property = Properties.query.filter_by(id=unit.properties).first()
    user_booking_count = Bookings.query.filter_by(user=current_user.email, is_active=True).count()
    if unit.tenant:
      flash(f"Unit is already occupied", category="danger")
      return redirect(url_for("main.unit_details", unit_id=unit.unique_id))
    elif unit.is_reserved:
      flash(f"Unit is already reserved. It will be available after 24 hrs", category="danger")
      return redirect(url_for("main.unit_details", unit_id=unit.unique_id))
    elif user_booking_count == 4:
      flash(f"You have reached your reservation limit of (4). To reserve more units wait for your current reservations to expire", category="info")
      return redirect(url_for("main.unit_details", unit_id=unit.unique_id))
    else:
      new_booking = Bookings(
        date = datetime.now(),
        expiry_date = datetime.now() + timedelta(days=1),
        property_id = unit_property.id,
        unit = unit.id,
        user = current_user.email,
      )
      db.session.add(new_booking)
      unit.is_reserved = True
      db.session.commit()
      flash(f"Unit reserved successfully", category="success")
      return redirect(url_for("main.reservations"))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("main.unit_details", unit_id=unit.unique_id))

@main.route("/unit-enquiry/<int:unit_id>", methods=["POST", "GET"])
@login_required
def unit_enquiry(unit_id):
  unit = Unit.query.filter_by(unique_id=unit_id).first()
  if not unit:
    flash("Unit not found", category="danger")
    return redirect(url_for('main.properties'))
  flash("Feature coming soon", category="info")
  return redirect(url_for('main.unit_enquiry', unit_id=unit.unique_id))

@main.route("/reservations")
@login_required
def reservations():
  reservations = Bookings.query.filter_by(user=current_user.email, is_active=True).all()
  properties = Properties.query.all()
  units = Unit.query.all()
  # expired_reservations = []
  # if booking:
  #   for overbook in booking:
  #     if overbook.user == current_user.id:
  #       reserved_property = Properties.query.filter_by(id=overbook.property_id).first()
  #     if overbook.expiry_date < datetime.now()and overbook.is_active == True:
  #       expired_reservations.append(overbook)
  #       unit = Unit.query.filter_by(id=overbook.unit).first()
  #       unit.is_reserved = False
  #       overbook.is_active = False
  #       db.session.commit()
  #   if len(expired_reservations) == 1:
  #     flash(f"One of your reservations has expired", category="info")
  #   elif len(expired_reservations) > 1:
  #     all_expired = len(expired_reservations)
  #     flash(f"{all_expired} of your reservations have expired", category="info")
  # else:
  #   return render_template("Main/reservations.html")
  
  return render_template("Main/reservations.html", reservations=reservations, units=units, properties=properties)

@main.route("/delete-reservation/<int:reservation_id>")
@login_required
def delete_reservation(reservation_id):
  reservation = Bookings.query.filter_by(unique_id=reservation_id).first()
  if not reservation:
    flash("No reservation found")
    return redirect(url_for('main.properties'))
  unit = Unit.query.filter_by(id=reservation.unit).first()
  if unit:
    unit.is_reserved = False
  db.session.delete(reservation)
  db.session.commit()
  flash(f"Reservation deleted successfully", category="success")
  return redirect(url_for('main.reservations'))
