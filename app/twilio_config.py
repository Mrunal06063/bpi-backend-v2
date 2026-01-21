import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
VERIFY_SERVICE_SID = os.getenv("VERIFY_SERVICE_SID")

if not ACCOUNT_SID or not AUTH_TOKEN or not VERIFY_SERVICE_SID:
    raise RuntimeError("Twilio environment variables not set")

client = Client(ACCOUNT_SID, AUTH_TOKEN)
