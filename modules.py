from models import *
from datetime import datetime, date
from twilio.rest import Client
import random, os

account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)

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

def generate_invoice_landlord(current_user):
  units = Unit.query.filter(Unit.landlord == current_user, Unit.tenant != None).all()
  if units:
    for unit in units:
      unit_transactions = Transaction.query.filter_by(Unit=unit.id).all()
      if unit_transactions:
        if unit_transactions[-1].next_date == date.today():
          invoice = Invoice.query.filter_by(unit=unit.id, status="Active").first()
          if invoice:
            pass
          else:
            invoice_logic(unit.tenant, unit.id, unit.rent_amount)
      else:
        invoices = Invoice.query.filter_by(unit=unit.id, status="Active").all()
        if invoices:
          diff = datetime.now() - invoices[-1].date_created
          if diff.days == 30:
            invoice_logic(unit.tenant, unit.id, unit.rent_amount)
          else:
            pass
        else:
          invoice_logic(unit.tenant, unit.id, unit.rent_amount)

def generate_invoice_tenant(current_user):
  unit = db.session.query(Unit).filter(Unit.tenant == current_user).first()
  if unit:
    unit_transactions = Transaction.query.filter_by(Unit=unit.id).all()
    if unit_transactions:
      if unit_transactions[-1].next_date == date.today():
        invoice = Invoice.query.filter_by(unit=unit.id, status="Active").first()
        if invoice:
          pass
        else:
          invoice_logic(current_user, unit.id, unit.rent_amount)
    else:
      invoices = Invoice.query.filter_by(unit=unit.id, status="Active").all()
      if invoices:
        diff = datetime.now() - invoices[-1].date_created
        print(diff.days)
        if diff.days == 30:
          invoice_logic(current_user, unit.id, unit.rent_amount)
        else:
          pass
      else:
        invoice_logic(current_user, unit.id, unit.rent_amount)

def send_sms(message):
  messages = clients.messages \
    .create(
      to = '+254796897011',
      from_ = '+13254253790',
      body = message
    )
  print(messages)
