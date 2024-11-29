from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from Models.base_model import db
from Models.users import Landlord
from Models.unit import Unit, UnitMetrics
from Models.property import Properties
from Models.transactions import Transactions
from Models.complaints import Complaints
from Models.invoice import Invoice
from .form import *
from modules import generate_invoice, rent_transaction
from decorators import tenant_role_required
import os, stripe, datetime, locale
from datetime import datetime, date

locale.setlocale(locale.LC_ALL, 'en_US')
'en_US'

tenants = Blueprint("tenant", __name__, url_prefix="/tenant")
stripe.api_key = os.environ['Stripe_api_key']

@tenants.route("/tenant-dashboard")
@login_required
@tenant_role_required("Tenant")
def tenant_dashboard():
  landlord = db.session.query(Landlord).filter(current_user.landlord == Landlord.id).first()
  properties = Properties.query.filter_by(id = current_user.properties).first()
  unit = db.session.query(Unit).filter(Unit.tenant == current_user.id).first()
  unit_metrics = UnitMetrics.query.filter_by(unit=unit.id).first()
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
  
  return render_template ("Tenant/new_tenant_dashboard.html",landlord=landlord,unit=unit,properties=properties, transactions=transactions, today_time=today_time, invoices=invoices, unit_metrics=unit_metrics)

@tenants.route("/send-messages/<int:landlord_id>", methods=["POST","GET"])
@login_required
@tenant_role_required("Tenant")
def send_message(landlord_id):
  pass

@tenants.route("/rent-payment")
@login_required
@tenant_role_required("Tenant")
def rent_payment():
  invoice = Invoice.query.filter_by(tenant=current_user.id, status="Active").first()
  unit = Unit.query.filter_by(tenant=current_user.id).first()
  if unit.rent_amount > 999999:
    flash(f"Amount is to large to be processed by the system via bank", category="danger")
  elif invoice:
    checkout_session = stripe.checkout.Session.create(
      line_items = [
        {
          'price_data': {
            'currency': 'KES',
            'product_data': {
              'name': 'Rent Payment',
            },
            'unit_amount': (invoice.amount * 100),
          },
          'quantity': 1,
        }
      ],
      payment_method_types=["card"],
      mode='payment',
      success_url=request.host_url + 'tenant/payment-complete',
      cancel_url=request.host_url + '',
    )
    return redirect(checkout_session.url)
  else:
    flash(f"Could not find an invoice for your payment", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
  
  return redirect(url_for('tenant.tenant_dashboard'))

@tenants.route("/payment-complete")
@login_required
@tenant_role_required("Tenant")
def payment_complete():
  unit = Unit.query.filter_by(tenant=current_user.id).first()
  landlord = Landlord.query.filter_by(id=current_user.landlord).first()
  transactions = db.session.query(Transactions).filter(Transactions.tenant == current_user.id).all()
  invoice = Invoice.query.filter(Invoice.unit == unit.id, Invoice.status == "Active").first()
  new_transaction = {
    'tenant': current_user.id,
    'landlord': landlord.id,
    'properties': current_user.properties,
    'unit': unit.id,
    'invoice': invoice.id,
    'origin': "Bank"
  }
  if transactions:
    if not invoice:
      flash(f"You've already paid this month's rent, wait until next charge", category="danger")
      return redirect(url_for('tenant.tenant_dashboard'))
    else:
      rent_transaction(**new_transaction)
      invoice.date_closed = datetime.now()
      invoice.month_created = datetime.now()
      invoice.status = "Cleared"
      db.session.commit()
      flash(f'Payment complete, transaction recorded, invoice cleared', category="success")
      return redirect(url_for('tenant.tenant_dashboard'))
  else:
    rent_transaction(**new_transaction)
    invoice.date_closed = datetime.now()
    invoice.month_created = datetime.now()
    invoice.status = "Cleared"
    db.session.commit()
    flash(f'Payment complete, transaction recorded, invoice cleared', category="success")

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
