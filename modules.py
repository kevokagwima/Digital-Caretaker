from flask import flash
from models import *
from datetime import datetime, date
from twilio.rest import Client
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
import random, os

account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)
sg = SendGridAPIClient(os.environ['Email_api_key'])

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

def send_email(email):
  message = Mail(
    from_email="kevinkagwima4@gmail.com",
    to_emails="kevokagwima@gmail.com",
    subject="Property Management System",
    html_content=email
  )
  response = sg.send(message)
  print(response)

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
