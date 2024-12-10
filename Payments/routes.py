from flask import Blueprint, flash, request, redirect, url_for, jsonify, render_template
from flask_login import login_required, current_user
from decorators import tenant_role_required
from modules import rent_transaction
from Models.base_model import db
from Models.users import Landlord, Tenant
from Models.transactions import Transactions, Payment
from Models.invoice import Invoice
from Models.unit import Unit
from .mpesa import LipanaMpesaPpassword
from datetime import datetime, timedelta
import os, stripe, pytz, requests, base64

payments = Blueprint("payment", __name__, url_prefix="/payment")
stripe.api_key = os.environ['Stripe_api_key']
utc_timezone = pytz.utc
utc_now = datetime.now(utc_timezone) + timedelta(hours=3)

@payments.route("/card")
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
      success_url=request.host_url + 'payment/payment-complete',
      cancel_url=request.host_url + '',
    )
    return redirect(checkout_session.url)
  else:
    flash(f"Could not find an invoice for your payment", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
  
  return redirect(url_for('tenant.tenant_dashboard'))

@payments.route("/payment-complete")
@login_required
@tenant_role_required("Tenant")
def card_payment_complete():
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

def getAccessToken():
  consumer_key = os.environ.get("consumer_key")
  consumer_secret = os.environ.get("consumer_secret")
  api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

  try:
    encoded_credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

    headers = {
      "Authorization": f"Basic {encoded_credentials}",
      "Content-Type": "application/json"
    }

    response = requests.get(api_URL, headers=headers).json()

    if "access_token" in response:
      return response["access_token"]
    else:
      raise Exception("Failed to get access token: " + response["error_description"])
  except Exception as e:
    raise Exception("Failed to get access token: " + str(e))

def register_url(access_token):
  api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"

  headers = {
    "Authorization": "Bearer %s" % access_token,
    "Content-Type": "application/json"
  }

  payload = {
    "ShortCode": "174379",
    "ResponseType": "Completed",
    "ConfirmationURL": "https://990d-41-80-119-29.ngrok-free.app/payment/confirm-payment/",
    "ValidationURL": "https://mydomain.com/validation"
  }

  try:
    response = requests.request("POST", api_url, headers=headers, json=payload)
    return response
  except Exception as e:
    print(f"Error: {repr(e)}")

def process_stk_push(access_token, amount, phone_number):
  api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

  headers = {
    "Authorization": "Bearer %s" % access_token,
    "Content-Type": "application/json"
  }

  request = {
    "BusinessShortCode": "174379",
    "Password": LipanaMpesaPpassword.online_password,
    "Timestamp": LipanaMpesaPpassword.lipa_time,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": f"254{phone_number}",
    "PartyB": "174379",
    "PhoneNumber": f"254{phone_number}",
    "checkout_url": "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    "CallBackURL": "https://990d-41-80-119-29.ngrok-free.app/payment/confirm-payment/",
    "AccountReference": "PMS",
    "TransactionDesc": "Rent Payment"
  }

  try:
    response = requests.post(api_url, json=request, headers=headers)
    return response
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('main.book'))

@payments.route("/mpesa/<int:invoice_id>")
@login_required
@tenant_role_required("Tenant")
def stk_push(invoice_id):
  # try:
  invoice = Invoice.query.filter_by(unique_id=invoice_id).first()
  if not invoice:
    flash("You have no active invoice", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))

  access_token = getAccessToken()
  phone_number = current_user.phone
  amount = invoice.amount
  register_response = register_url(access_token)
  response = process_stk_push(access_token, amount, phone_number)
  response_data = response.json()
  print(register_response.text)
  print(response.text)

  if response.status_code != 200:
    flash("Could not initiate payment. Try again", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
  else:
    existing_payment = Payment.query.filter_by(invoice=invoice.id).first()
    if existing_payment:
      existing_payment.is_pending = False
      existing_payment.is_failed = True
      db.session.commit()
    new_payment = Payment(
      MerchantRequestID = response_data["MerchantRequestID"],
      CheckoutRequestID = response_data["CheckoutRequestID"],
      amount = amount,
      phone_number = phone_number,
      invoice = invoice.id
    )
    db.session.add(new_payment)
    db.session.commit()
    flash("An stk push has been sent to your phone. Enter your pin to complete the payment", category="success")
    return redirect(url_for('payment.verify_payment', invoice_id=invoice.unique_id))
  # except Exception as e:
  #   flash(f"{repr(e)}", category="danger")
  #   return redirect(url_for('tenant.tenant_dashboard'))

@payments.route("/verify/<int:invoice_id>")
def verify_payment(invoice_id):
  invoice = Invoice.query.filter_by(unique_id=invoice_id).first()
  if not invoice:
    flash("You have no active invoice", category="danger")
    return redirect(url_for('tenant.tenant_dashboard'))
  payments = Payment.query.filter_by(invoice=invoice.id).all()

  return render_template("Payment/verify-payment.html", payment=payments[-1], invoice=invoice)

@payments.route("/confirm-payment/", methods=["POST"])
def confirm_payment():
  try:
    json_data = request.json
    print(json_data)
    stk_callback = json_data['Body']['stkCallback']
    merchant_request_id = stk_callback['MerchantRequestID']
    checkout_request_id = stk_callback['CheckoutRequestID']
    result_code = stk_callback['ResultCode']
    payment = Payment.query.filter_by(MerchantRequestID=merchant_request_id, CheckoutRequestID=checkout_request_id).first()
    if payment:
      if result_code != 0:
        payment_failed(payment.id)
        error_message = stk_callback['ResultDesc']
        response_data = {'ResultCode': result_code, 'ResultDesc': error_message}
        return jsonify(response_data)
      else:
        mpesa_receipt_number = next(item['Value'] for item in stk_callback['CallbackMetadata']['Item'] if item['Name'] == 'MpesaReceiptNumber')
        transation_date = next(item['Value'] for item in stk_callback['CallbackMetadata']['Item'] if item['Name'] == 'TransactionDate')
        payment_complete(payment.id, mpesa_receipt_number, transation_date)
        return jsonify({"ResultCode": result_code, "ResultDesc": "Success processing payment"}), 200
        
    else:
      print("No payment record")
  except Exception as e:
    print(f"Error processing payment: {repr(e)}")
    return jsonify({"ResultDesc": "Error processing payment"}), 400

def payment_complete(payment_id, mpesa_receipt_number, transaction_date):
  try:
    payment = Payment.query.get(payment_id)
    invoice = Invoice.query.get(payment.invoice)
    tenant = Tenant.query.get(invoice.tenant)
    payment.MpesaReceiptNumber = mpesa_receipt_number
    payment.is_pending = False
    payment.is_confirmed = True
    payment.transactionDate = datetime.strptime(str(transaction_date), "%Y%m%d%H%M%S")
    invoice.date_closed = datetime.strptime(str(transaction_date), "%Y%m%d%H%M%S")
    invoice.status = "Cleared"
    new_transaction = {
      'tenant': tenant.id,
      'landlord': tenant.landlord,
      'properties': tenant.properties,
      'unit': tenant.unit,
      'invoice': invoice.id,
      'origin': "Mpesa"
    }
    rent_transaction(**new_transaction)
    db.session.commit()
    print("Payment Complete")
    return jsonify("Success processing payment"), 200
  except Exception as e:
    print(f"{repr(e)}")
    return None

def payment_failed(payment_id):
  try:
    payment = Payment.query.get(payment_id)
    payment.transactionDate = utc_now
    payment.is_pending = False
    payment.is_failed = True
    db.session.commit()
    print("Payment Failed")
    return jsonify("Failed processing payment"), 200
  except Exception as e:
    print(f"{repr(e)}")
    return None
