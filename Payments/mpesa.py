from dotenv import load_dotenv
from datetime import datetime
import base64, os

load_dotenv()

class LipanaMpesaPpassword:
  consumer_key = os.environ.get("consumer_key")
  consumer_secret = os.environ.get("consumer_secret")
  lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
  Business_short_code = "174379"
  passkey = os.environ.get("passkey")
  data_to_encode = Business_short_code + passkey + lipa_time
  online_password = base64.b64encode(data_to_encode.encode()).decode("utf-8")
