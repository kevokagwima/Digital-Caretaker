from flask import Blueprint, flash, request, redirect, url_for, jsonify, render_template
from flask_login import login_required, current_user
from Models.base_model import db, get_local_time
from Models.transactions import Payment
from .mpesa import LipanaMpesaPpassword
import os, requests, base64

payments = Blueprint("payment", __name__, url_prefix="/payment")

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
    "ConfirmationURL": "https://1f17-41-206-42-66.ngrok-free.app/payment/confirm-payment/",
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
    "CallBackURL": "https://1f17-41-206-42-66.ngrok-free.app/payment/confirm-payment/",
    "AccountReference": "PMS",
    "TransactionDesc": "Rent Payment"
  }

  try:
    response = requests.post(api_url, json=request, headers=headers)
    return response
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for('main.book'))

@payments.route("/confirm-payment/", methods=["POST"])
def confirm_payment():
  try:
    json_data = request.json
    stk_callback = json_data['Body']['stkCallback']
    merchant_request_id = stk_callback['MerchantRequestID']
    checkout_request_id = stk_callback['CheckoutRequestID']
    result_code = stk_callback['ResultCode']
    payment = Payment.query.filter_by(MerchantRequestID=merchant_request_id, CheckoutRequestID=checkout_request_id).first()
    if payment:
      if result_code != 0:
        error_message = stk_callback['ResultDesc']
        response_data = {'ResultCode': result_code, 'ResultDesc': error_message}
        return jsonify(response_data)
      else:
        mpesa_receipt_number = next(item['Value'] for item in stk_callback['CallbackMetadata']['Item'] if item['Name'] == 'MpesaReceiptNumber')
        transation_date = next(item['Value'] for item in stk_callback['CallbackMetadata']['Item'] if item['Name'] == 'TransactionDate')
        return jsonify({"ResultCode": result_code, "ResultDesc": "Success processing payment"}), 200
    else:
      print("No payment record")
  except Exception as e:
    print(f"Error processing payment: {repr(e)}")
    return jsonify({"ResultDesc": "Error processing payment"}), 400
