from flask import Blueprint, render_template, flash, url_for, redirect, request, abort
from flask_login import login_required, fresh_login_required, current_user
from Models.models import db, Landlord, Unit, Transaction, Complaints, Invoice
from .form import *
from modules import generate_invoice, rent_transaction
import os, stripe, datetime, locale
from datetime import datetime, date

locale.setlocale(locale.LC_ALL, 'en_US')
'en_US'

tenants = Blueprint("tenant", __name__)
stripe.api_key = os.environ['Stripe_api_key']

@tenants.route("/tenant-dashboard")
@login_required
def tenant_dashboard():
  if current_user.account_type != "Tenant":
    abort(403)
  landlord = db.session.query(Landlord).filter(current_user.landlord == Landlord.id).first()
  properties = Properties.query.filter_by(id = current_user.properties).first()
  unit = db.session.query(Unit).filter(Unit.tenant == current_user.id).first()
  transactions = db.session.query(Transaction).filter(Transaction.tenant == current_user.id).all()
  today_time = date.today()
  invoices = Invoice.query.filter_by(tenant=current_user.id, status="Active").all()
  if unit:
    generate_invoice(unit.id, current_user.id, unit.rent_amount)
  if invoices:
    if len(invoices) == 1:
      flash(f"You have {len(invoices)} active invoice", category="info")
    else:
      flash(f"You have {len(invoices)} active invoices", category="info")
  
  return render_template ("new_tenant_dashboard.html",landlord=landlord,unit=unit,properties=properties, transactions=transactions, today_time=today_time, invoices=invoices)

@tenants.route("/send-messages/<int:landlord_id>", methods=["POST","GET"])
@fresh_login_required
@login_required
def send_message(landlord_id):
  pass

@tenants.route("/invoice-email/<int:invoice_id>")
@fresh_login_required
@login_required
def invoice_email(invoice_id):
  pass

@tenants.route("/rent-payment")
@fresh_login_required
@login_required
def rent_payment():
  if current_user.account_type != "Tenant":
    abort(403)
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
      success_url=request.host_url + 'payment-complete',
      cancel_url=request.host_url + '',
    )
    return redirect(checkout_session.url)
  else:
    flash(f"Could not find an invoice for your payment", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
  
  return redirect(url_for('tenant.tenant_dashboard'))

@tenants.route("/payment-complete")
@fresh_login_required
@login_required
def payment_complete():
  if current_user.account_type != "Tenant":
    abort(403)
  unit = Unit.query.filter_by(tenant=current_user.id).first()
  landlord = Landlord.query.filter_by(id=current_user.landlord).first()
  transactions = db.session.query(Transaction).filter(Transaction.tenant == current_user.id).all()
  invoice = Invoice.query.filter(Invoice.unit == unit.id, Invoice.status == "Active").first()
  new_transaction = {
    'tenant': current_user.id,
    'landlord': current_user.landlord,
    'Property': current_user.properties,
    'Unit': unit.id,
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

@tenants.route("/choose-file-to-upload", methods=['GET', 'POST'])
@login_required
def upload_file():
  pass

@tenants.route("/upload-mpesa-transaction")
@login_required
def upload_screenshot(image):
  pass

@tenants.route("/complaints", methods=["POST", "GET"])
@fresh_login_required
@login_required
def complaint():
  if current_user.account_type != "Tenant":
    abort(403)
  landlord = Landlord.query.get(current_user.landlord)
  try:
    new_complaint = Complaints(
      title=request.form.get("title"),
      category=request.form.get("category"),
      body=request.form.get("body"),
      date=datetime.now(),
      time=datetime.now(),
      tenant=current_user.id,
      landlord=Landlord.query.filter_by(id=current_user.landlord).first().id,
      Property=Properties.query.filter_by(id=current_user.properties).first().id
    )
    db.session.add(new_complaint)
    db.session.commit()
    flash(f"Complaint sent", category="success")
    return redirect(url_for("tenant.tenant_dashboard"))
  except:
    flash(f"Something went wrong. Try Again", category="danger")
    return redirect(url_for("tenant.tenant_dashboard"))
