from flask import Blueprint, render_template, flash, url_for, redirect, request, abort
from flask_login import login_user, login_required, fresh_login_required, logout_user, current_user
from models import Messages, db, Tenant, Landlord, Unit, Transaction, Verification, Complaints, Invoice
from .form import *
from modules import generate_invoice, send_sms, send_email, send_chat, rent_transaction
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import random, os, stripe, datetime, locale, time
from datetime import datetime, date

UPLOAD_FOLDER = 'Static/css/Images/Screenshots'
UPLOAD_FOLDER = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
locale.setlocale(locale.LC_ALL, 'en_US')
'en_US'

tenants = Blueprint("tenant", __name__)
stripe.api_key = os.environ['Stripe_api_key']

@tenants.route("/tenant_registration", methods=["POST", "GET"])
def tenant():
  form = tenant_form()
  try:
    if form.validate_on_submit():
      new_tenant = Tenant(
        first_name=form.first_name.data,
        second_name=form.second_name.data,
        last_name=form.last_name.data,
        email=form.email_address.data,
        phone=form.phone_number.data,
        username=form.username.data,
        date=datetime.now(),
        tenant_id=random.randint(100000, 999999),
        passwords=form.password.data,
        active="True",
        account_type="Tenant",
        landlord=Landlord.query.filter_by(landlord_id=form.landlord_id.data).first().id,
        properties=Properties.query.filter_by(property_id=form.property_id.data).first().id,
      )
      db.session.add(new_tenant)
      db.session.commit()
      message = {
        'receiver': new_tenant.email,
        'subject': 'Account Created Successfully',
        'body': f'Congratulations! {new_tenant.first_name} {new_tenant.second_name} you have successfully created your tenant account. \nLogin to your dashboard using your Tenant ID {new_tenant.tenant_id} and your password. \nDo not share your Tenant ID with anyone.'
      }
      # send_sms(message)
      send_email(**message)
      flash(f"Account created successfully", category="success")
      return redirect(url_for("tenant.tenant_login"))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the account {err_msg}",category="danger")
  except:
    flash(f"Something went wrong. Check the form and try again", category="danger")

  return render_template("tenant.html", form=form)

@tenants.route("/tenant_authentication", methods=["POST", "GET"])
def tenant_login():
  form = tenant_login_form()
  try:
    if form.validate_on_submit():
      tenant = Tenant.query.filter_by(tenant_id=form.tenant_id.data).first()
      if tenant and tenant.active == "True" and tenant.check_password_correction(attempted_password=form.password.data):
        login_user(tenant, remember=True)
        flash(f"Login successfull, welcome {tenant.username}",category="success")
        return redirect(url_for("tenant.tenant_dashboard"))
      elif tenant == None:
        flash(f"No user with that Tenant ID", category="danger")
        return redirect(url_for('tenant.tenant_login'))
      elif tenant.active != "True":
        flash(f"Your account is no longer active, contact ICT support", category="danger")
        return redirect(url_for('tenant.tenant_login'))
      else:
        flash(f"Invalid credentials", category="danger")
        return redirect(url_for('tenant.tenant_login'))
  except:
    flash(f"Something went wrong, try again", category="danger")
    return redirect(url_for('tenant.tenant_login'))

  return render_template("tenant_login.html", form=form)

@tenants.route("/tenant_dashboard")
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
  landlord = Landlord.query.get(landlord_id)
  messages = Messages.query.filter_by(landlord=landlord.id, tenant=current_user.id).all()
  if request.method == "POST":
    new_message = {
      'landlord': landlord.id,
      'tenant': current_user.id,
      'info': request.form.get("message"),
      'author': current_user.account_type
    }
    send_chat(**new_message)
    return redirect(url_for('tenant.send_message', landlord_id=landlord.id))

  return render_template("message.html", messages=messages, landlord=landlord)

@tenants.route("/invoice-email/<int:invoice_id>")
@fresh_login_required
@login_required
def invoice_email(invoice_id):
  invoice = Invoice.query.get(invoice_id)
  message = {
    'receiver': current_user.email,
    'subject': "Invoice",
    'body': f'Invoice #{invoice.invoice_id} of amount {locale.format("%d", invoice.amount, "en_US")} is pending, clear it to avoid penalties'
  }
  send_email(**message)
  flash("Invoice sent to email successfully", category="success")

  return redirect(url_for('tenant.tenant_dashboard'))

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
  landlord_message = {
    'receiver': [landlord.email, current_user.email],
    'subject': 'RENT PAYMENT',
    'body': f'Confirmed! rental payment of amount {locale.format("%d", unit.rent_amount, "en_US")} for unit {unit.name} - {unit.Type} paid successfully on {datetime.now().strftime("%d/%m/%Y")} by tenant {current_user.first_name} { current_user.second_name }.'
  }
  tenant_message = {
    'receiver': current_user.email,
    'subject': 'RENT PAYMENT',
    'body': f'Confirmed! You have cleared your rental payment of amount {locale.format("%d", unit.rent_amount, "en_US")} for unit {unit.name} - {unit.Type} paid successfully on {datetime.now().strftime("%d/%m/%Y")}.'
  }
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
      # send_sms(message)
      send_email(**landlord_message)
      # send_email(**tenant_message)
      return redirect(url_for('tenant.tenant_dashboard'))
  else:
    rent_transaction(**new_transaction)
    invoice.date_closed = datetime.now()
    invoice.month_created = datetime.now()
    invoice.status = "Cleared"
    db.session.commit()
    flash(f'Payment complete, transaction recorded, invoice cleared', category="success")
    # send_sms(message)
    send_email(**landlord_message)
    # send_email(**tenant_message)

  return redirect(url_for('tenant.tenant_dashboard'))

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@tenants.route("/choose-file-to-upload", methods=['GET', 'POST'])
@login_required
def upload_file():
  if current_user.account_type != "Tenant":
    abort(403)
  if request.method == 'POST':
    file = request.files['image']
    if file.filename == '':
      flash(f'No selected file', category="danger")
      return redirect(url_for('tenant.tenant_dashboard'))
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(UPLOAD_FOLDER, filename))
      upload_screenshot(file)
      
  return redirect(url_for('tenant.tenant_dashboard'))

@tenants.route("/upload-mpesa-transaction")
@login_required
def upload_screenshot(image):
  if current_user.account_type != "Tenant":
    abort(403)
  pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
  try:
    img = Image.open(image)
    text = pytesseract.image_to_string(img)
    verify = Verification.query.filter_by(tenant=current_user.id).first()
    if verify:
      verify.status = "pending"
      if text == '':
        flash(f"Could not generate text from the image provided", category="danger")
        return redirect(url_for('tenant.tenant_dashboard'))
      else:
        verify.info = text
      db.session.commit()
      flash(f"Upload successfull, awaiting landlord verification", category="success")
      return redirect(url_for('tenant.tenant_dashboard'))
    elif text == '':
      flash(f"Could not generate text from the image provided", category="danger")
      return redirect(url_for('tenant.tenant_dashboard'))
    else:
      verification = Verification (
        landlord = current_user.landlord,
        tenant = current_user.id,
        info = text,
        date = datetime.now(),
        status = "pending"
      )
      db.session.add(verification)
      db.session.commit()
      flash(f"Upload successfull, awaiting landlord verification", category="success")
      return redirect(url_for('tenant.tenant_dashboard'))
  except:
    flash(f"Upload failed, could not analyze the image", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))

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
    message = {
      'receiver': landlord.email,
      'subject': 'Tenant Complaint',
      'body': f'You have a new complaint from a tenant. \nTitle: {new_complaint.title} \nCategory: {new_complaint.category} \nThe complaint reads: \n{new_complaint.body}'
    }
    # send_sms(message)
    db.session.add(new_complaint)
    db.session.commit()
    send_email(**message)
    flash(f"Complaint sent", category="success")
    return redirect(url_for("tenant.tenant_dashboard"))
  except:
    flash(f"Something went wrong. Try Again", category="danger")
    return redirect(url_for("tenant.tenant_dashboard"))

@tenants.route("/logout_tenant")
@login_required
def tenant_logout():
  if current_user.account_type != "Tenant":
    abort(403)
  logout_user()
  flash(f"Logged out successfully!", category="success")
  return redirect(url_for("tenant.tenant_login"))
