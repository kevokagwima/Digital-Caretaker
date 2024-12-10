from flask import Blueprint, flash, request, redirect, url_for
from flask_login import login_required, current_user
from decorators import tenant_role_required
from modules import rent_transaction
from Models.base_model import db
from Models.users import Landlord
from Models.transactions import Transactions
from Models.invoice import Invoice
from Models.unit import Unit
from datetime import datetime
import os, stripe

payments = Blueprint("payment", __name__)
stripe.api_key = os.environ['Stripe_api_key']

@payments.route("/payment/card")
@login_required
@tenant_role_required("Tenant")
def card_payment():
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

@payments.route("/payment/mpesa")
@login_required
@tenant_role_required("Tenant")
def mpesa_payment():
  flash("Feature coming soon", category="info") 
  return redirect(url_for('tenant.tenant_dashboard'))

@payments.route("/payment-complete")
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
