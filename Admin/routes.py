from flask import Blueprint, render_template, flash, url_for, redirect, request, abort
from flask_login import login_required, current_user
from Models.models import *
from .form import *
from modules import assign_tenant_unit
import random
from datetime import date, datetime

admins = Blueprint("admin", __name__)
today = date.today()

@admins.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
  if current_user.account_type != "Admin":
    abort(403)
  properties = Properties.query.all()
  tenants = Tenant.query.all()
  users = Users.query.all()
  landlords = Landlord.query.all()
  reservations = Bookings.query.all()
  transactions = Transaction.query.all()
  units = Unit.query.all()
  complaints = Complaints.query.order_by(Complaints.time.desc()).all()
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
  extras = Extras.query.all()
  invoices = Invoice.query.all()
  today_time = today
  form = Extra_signup()
  if form.validate_on_submit():
    add_extras(form)
    return redirect(url_for('admin.admin'))
  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"There was an error creating the user: {err_msg}", category="danger")

  return render_template("admin.html",properties=properties,tenants=tenants,landlords=landlords,users=users, units=units, complaints=complaints, extras=extras, today_time=today_time, form=form, reservations=reservations, transactions=transactions, invoices=invoices, all_users=all_users)

@admins.route("/admin/assign-landlord/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def admin_assign_landlord(tenant_id):
  if current_user.account_type != "Admin":
    abort(403)
  try:
    if request.method == "POST":
      landlord_id = request.form.get("landlord-assign")
      tenant = Tenant.query.filter_by(unique_id=tenant_id).first()
      landlord = Landlord.query.filter_by(unique_id=landlord_id).first()
      if tenant and landlord:
        tenant.landlord = landlord.id
        tenant.is_active = True
        db.session.commit()
        flash(f"Tenant Landlord Information Updated Successfully", category="success")
      return redirect(url_for('admin.admin'))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('admin.admin'))

@admins.route("/admin/Assign-property/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def admin_assign_property(tenant_id):
  if current_user.account_type != "Admin":
    abort(403)
  property_id = request.form.get("assign-property")
  try:
    tenant = Tenant.query.filter_by(unique_id=tenant_id).first()
    Property = Properties.query.filter_by(property_id=property_id).first()
    if tenant and Property:
      tenant.properties = Property.id
      db.session.commit()
      flash(f"Tenant Property Information Updated Successfully", category="success")
    return redirect(url_for('admin.admin'))
  except:
    flash(f"An Error Occurred. Try again later", category="danger")
    return redirect(url_for('admin.admin'))

@admins.route("/admin/Assign-unit/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def admin_assign_unit(tenant_id):
  if current_user.account_type != "Admin":
    abort(403)
  unit_id = request.form.get("assign-unit")
  try:
    tenant = Tenant.query.filter_by(unique_id=tenant_id).first()
    unit = Unit.query.filter_by(unit_id=unit_id).first()
    previous_url = request.referrer
    assign_tenant_unit(tenant.id, unit.id, tenant.properties, previous_url, tenant.landlord)
    return redirect(url_for('admin.admin'))
  except:
    flash(f"An Error Occurred", category="danger")
  return redirect(url_for('admin.admin'))

@admins.route("/admin/revoke-tenant/<int:tenant_id>", methods=["POST", "GET"])
@login_required
def admin_revoke_tenant(tenant_id):
  if current_user.account_type != "Admin":
    abort(403)
  try:
    tenant = Tenant.query.filter_by(unique_id=tenant_id).first()
    if tenant.is_active==False:
      flash(f"Tenant's account already revoked", category="info")
      return redirect(url_for('admin.admin'))
    elif tenant:
      tenant.landlord = None
      tenant.properties = None
      tenant.is_active = False
      if tenant.unit:
        unit = Unit.query.filter_by(tenant=tenant.id).all()
        for units in unit:
          units.tenant = None
      db.session.commit()
      flash(f"Tenant revoked successfully", category="success")
    return redirect(url_for('admin.admin'))
  except:
    flash(f"An Error Occurred", category="danger")
    return redirect(url_for('admin.admin'))

@admins.route("/add-extra-personell", methods=["POST", "GET"])
@login_required
def add_extras(form):
  if current_user.account_type != "Admin":
    abort(403)
  new_extra = Extras(
    extra_id = random.randint(100000, 999999),
    first_name = form.first_name.data,
    last_name = form.last_name.data,
    age = form.age.data,
    phone = form.phone_number.data,
    email = form.email_address.data,
    title = form.title.data,
    cost = form.cost.data,
    date = datetime.now()
  )
  db.session.add(new_extra)
  db.session.commit()
  flash(f"Successful registration of a new Extra", category="success")
  return redirect(url_for('admin.admin'))

@admins.route("/admin/delete-complaint/<int:complaint_id>")
@login_required
def delete_complaint(complaint_id):
  if current_user.account_type != "Admin":
    abort(403)
  complaint = Complaints.query.get(complaint_id)
  tenant = Tenant.query.filter_by(id=complaint.tenant).first()
  if complaint:
    db.session.delete(complaint)
    db.session.commit()
    flash(f"Complaint deleted successfully", category="success")
    return redirect(url_for('admin.admin'))
  else:
    flash(f"Complaint not found", category="danger")
    return redirect(url_for('admin.admin'))
