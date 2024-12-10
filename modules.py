from flask import flash, redirect, url_for
from Models.base_model import db
from Models.users import Tenant
from Models.complaints import Complaints
from Models.invoice import Invoice
from Models.bookings import Bookings
from Models.unit import Unit
from Models.transactions import Transactions
from datetime import datetime, date, timedelta

def invoice_logic(tenant, unit_id, rent):
  new_invoice = Invoice(
    tenant = tenant,
    unit = unit_id,
    amount = rent,
    date_created = datetime.now(),
    month_created = date.today(),
    status = "Active"
  )
  db.session.add(new_invoice)
  db.session.commit()

def generate_invoice(unit_id, unit_tenant, unit_rent):
  unit_transactions = Transactions.query.filter_by(unit=unit_id).all()
  if unit_transactions:
    if unit_transactions[-1].next_date <= date.today():
      invoice = Invoice.query.filter_by(unit=unit_id, status="Active").first()
      if not invoice:
        invoice_logic(unit_tenant, unit_id, unit_rent)
  else:
    invoices = Invoice.query.filter_by(unit=unit_id, status="Active").all()
    if invoices:
      if invoices[-1].date_created.strftime("%m") < datetime.now().strftime("%m"):
        invoice_logic(unit_tenant, unit_id, unit_rent)
    else:
      invoice_logic(unit_tenant, unit_id, unit_rent)

def send_sms(message):
  pass

def send_email(**email):
  pass

def check_reservation_expiry(property_id):
  reservations = Bookings.query.filter_by(property_id=property_id).all()
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

def send_chat(**message):
  pass

def assign_tenant_unit(tenant_id, unit_id):
  try:
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    unit = Unit.query.filter_by(id=unit_id).first()
    unit.tenant = tenant.id
    db.session.commit()
    flash(f"Unit {unit.name} - {unit.unit_type} assigned to {tenant.first_name} {tenant.last_name} successfully", category="success")
    generate_invoice(unit.id, unit.tenant, unit.rent_amount)
  except Exception as e:
    flash(f"{repr(e)}", category="danger")

def revoke_tenant_access(tenant_id):
  try:
    tenant = Tenant.query.get(tenant_id)
    if tenant.unit:
      unit = db.session.query(Unit).filter(tenant.id == Unit.tenant).first()
      unit.tenant = None
    if tenant.complaint:
      complaints = Complaints.query.filter(Complaints.tenant == tenant.id).all()
      for complaint in complaints:
        db.session.delete(complaint)
    if tenant.invoice:
      invoices = Invoice.query.filter(Invoice.tenant == tenant.id).all()
      for invoice in invoices:
        invoice.status = "Cancelled"
        db.session.commit()
    tenant.is_active = False
    tenant.landlord = None
    tenant.properties = None
    db.session.commit()
    flash(f"Tenant removed successfully",category="success")
  except Exception as e:
    flash(f"{repr(e)}", category="danger")

def rent_transaction(**transaction):
  try:
    new_transaction = Transactions(
      tenant = transaction["tenant"],
      landlord = transaction["landlord"],
      properties = transaction["properties"],
      unit = transaction["unit"],
      date = datetime.now(),
      time = datetime.now(),
      next_date = datetime.now() + timedelta(days=30),
      invoice = transaction["invoice"],
      origin = transaction["origin"]
    )
    db.session.add(new_transaction)
    db.session.commit()
  except Exception as e:
    flash(f'{repr(e)}', category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
