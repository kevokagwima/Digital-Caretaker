from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from Models.base_model import db
from Models.users import Landlord
from Models.unit import Unit
from Models.property import Properties
from Models.transactions import Transactions
from Models.complaints import Complaints
from Models.invoice import Invoice
from .form import *
from modules import generate_invoice
from decorators import tenant_role_required
import datetime, locale
from datetime import datetime, date

locale.setlocale(locale.LC_ALL, 'en_US')
'en_US'

tenants = Blueprint("tenant", __name__, url_prefix="/tenant")

@tenants.route("/dashboard")
@login_required
@tenant_role_required("Tenant")
def tenant_dashboard():
  landlord = db.session.query(Landlord).filter(current_user.landlord == Landlord.id).first()
  properties = Properties.query.filter_by(id = current_user.properties).first()
  unit = db.session.query(Unit).filter(Unit.tenant == current_user.id).first()
  transactions = db.session.query(Transactions).filter(Transactions.tenant == current_user.id).all()
  today_time = date.today()
  invoices = Invoice.query.filter_by(tenant=current_user.id, status="Active").all()
  if unit:
    generate_invoice(unit.id, current_user.id, unit.rent_amount)
  if invoices:
    if len(invoices) == 1:
      flash(f"You have {len(invoices)} active invoice", category="info")
    else:
      flash(f"You have {len(invoices)} active invoices", category="info")
  
  return render_template ("Tenant/new_tenant_dashboard.html",landlord=landlord,unit=unit,properties=properties, transactions=transactions, today_time=today_time, invoices=invoices)

@tenants.route("/send-messages/<int:landlord_id>", methods=["POST","GET"])
@login_required
@tenant_role_required("Tenant")
def send_message(landlord_id):
  flash("Feature coming soon", category="info")
  return redirect(url_for('tenant.tenant_dashboard'))

@tenants.route("/send-complaint", methods=["POST", "GET"])
@login_required
@tenant_role_required("Tenant")
def send_complaint():
  try:
    form = ComplaintForm()
    if form.validate_on_submit():
      new_complaint = Complaints(
        title=request.form.get("title"),
        category=request.form.get("category"),
        message=request.form.get("message"),
        date=datetime.now(),
        time=datetime.now(),
        tenant=current_user.id,
        landlord=Landlord.query.filter_by(id=current_user.landlord).first().id,
        properties=Properties.query.filter_by(id=current_user.properties).first().id
      )
      db.session.add(new_complaint)
      db.session.commit()
      flash(f"Complaint sent", category="success")
      return redirect(url_for("tenant.tenant_dashboard"))
    
    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")
        return redirect(url_for('tenant.send_complaint'))

    return render_template("Tenant/complaint.html", form=form)
  except Exception as e:
    flash(f"Error. {repr(e)}", category="danger")
    return redirect(url_for("tenant.tenant_dashboard"))
