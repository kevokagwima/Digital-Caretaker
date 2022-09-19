from flask import flash, redirect, url_for
from email.message import EmailMessage
from models import *
from datetime import datetime, date, timedelta
from twilio.rest import Client
import random, os, random, ssl, smtplib

account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)
email_sender = os.environ["Email_from"]
email_password = os.environ["Email_password"]
em = EmailMessage()

def invoice_logic(tenant, unit_id, rent):
  new_invoice = Invoice(
    invoice_id = random.randint(100000,999999),
    tenant = tenant,
    unit = unit_id,
    amount = rent,
    date_created = datetime.now(),
    status = "Active"
  )
  db.session.add(new_invoice)
  db.session.commit()

def generate_invoice(unit_id, unit_tenant, unit_rent):
  unit_transactions = Transaction.query.filter_by(Unit=unit_id).all()
  if unit_transactions:
    if unit_transactions[-1].next_date == date.today():
      invoice = Invoice.query.filter_by(unit=unit_id, status="Active").first()
      if invoice:
        pass
      else:
        invoice_logic(unit_tenant, unit_id, unit_rent)
  else:
    invoices = Invoice.query.filter_by(unit=unit_id, status="Active").all()
    if invoices:
      diff = datetime.now() - invoices[-1].date_created
      if diff.days == 30:
        invoice_logic(unit_tenant, unit_id, unit_rent)
      else:
        pass
    else:
      invoice_logic(unit_tenant, unit_id, unit_rent)

def send_sms(message):
  messages = clients.messages \
    .create(
      to = '+254796897011',
      from_ = '+13254253790',
      body = message
    )
  print(messages)

def send_email(**email):
  em['sender'] = email_sender
  em['to'] = email["receiver"]
  em['subject'] = email["subject"]
  em.set_content(email["body"])
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    try:
      smtp.login(email_sender, email_password)
      smtp.sendmail(email_sender, email["receiver"], em.as_string())
    except:
      flash("Email failed to send", category="danger")

def check_reservation_expiry(property_id):
  reservations = Bookings.query.filter_by(property=property_id).all()
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
  try:
    new_message = Messages(
      landlord = message["landlord"],
      tenant = message["tenant"],
      info = message["info"],
      author = message["author"],
      date = datetime.now()
    )
    db.session.add(new_message)
    db.session.commit()
  except:
    flash(f"An error occured", category="danger")

def assign_tenant_unit(tenant_id, unit_id, property_id, previous_url, current_user):
  try:
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    unit = Unit.query.filter_by(id=unit_id).first()
    if tenant.landlord != current_user:
      flash(f"Unknown Tenant ID. Try again", category="info")
      return redirect(previous_url)
    elif tenant.properties == None:
      flash(f"No property is assigned to the tenant", category="info")
      return redirect(previous_url)
    elif tenant.properties != property_id:
      flash(f"Cannot assign a unit to a tenant from a different property", category="info")
      return redirect(previous_url)
    elif unit.landlord != current_user:
      flash(f"Unknown Unit ID. Try again", category="info")
      return redirect(previous_url)
    elif unit.Property != property_id:
      flash(f"Cannot assign a tenant a unit from a different property", category="info")
      return redirect(previous_url)
    elif tenant and unit:
      if tenant.unit or unit.tenant or unit.reserved == "True":
        flash(f"Could not assign unit. Unit already occupied or reserved or tenant has a unit. Try again",category="danger")
      elif tenant.active == "False":
        flash(f"Cannot assign unit, tenant is not active", category="danger")
        return redirect(previous_url)
      else:
        unit.tenant = tenant.id
        db.session.commit()
        flash(f"Unit {unit.name} - {unit.Type} assigned to {tenant.first_name} {tenant.second_name} successfully",category="success")
        generate_invoice(unit.id, unit.tenant, unit.rent_amount)
        return redirect(url_for('landlord.tenant_details', tenant_id=tenant_id))
  except:
    flash(f"Invalid Tenant ID or Unit ID. Try again",category="danger")
    return redirect(previous_url)

def revoke_tenant_access(tenant_id, current_user, previous_url):
  try:
    tenant = Tenant.query.get(tenant_id)
    if tenant.landlord != current_user:
      flash(f"Unknown Tenant ID", category="info")
      return redirect(previous_url)
    elif tenant.active == "False":
      flash(f"{tenant.first_name} {tenant.second_name}'s Account is already revoked",category="danger")
      return redirect(previous_url)
    elif tenant:
      if tenant.unit:
        unit = db.session.query(Unit).filter(tenant.id == Unit.tenant).first()
        unit.tenant = None
      elif tenant.invoice:
        invoices = Invoice.query.filter(Invoice.tenant == tenant.id, Invoice.status == "Active").all()
        for invoice in invoices:
          db.session.delete(invoice)
      tenant.active = "False"
      tenant.landlord = None
      tenant.properties = None
      db.session.commit()
      flash(f"{tenant.first_name} {tenant.second_name}'s Account Revoked successfully. Tenant no longer part of your tenant list.",category="success")
  except:
    flash(f"An error occurred, try again later", category="danger")
    return redirect(previous_url)

def rent_transaction(**transaction):
  try:
    new_transaction = Transaction(
      tenant = transaction["tenant"],
      landlord = transaction["landlord"],
      Property = transaction["Property"],
      Unit = transaction["Unit"],
      date = datetime.now(),
      time = datetime.now(),
      next_date = datetime.now() + timedelta(days=30),
      transaction_id = random.randint(100000, 999999),
      invoice = transaction["invoice"],
      origin = transaction["origin"]
    )
    db.session.add(new_transaction)
    db.session.commit()
  except:
    flash(f'Payment could not be processed', category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
