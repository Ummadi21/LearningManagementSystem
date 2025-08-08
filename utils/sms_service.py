from twilio.rest import Client
import os

def send_sms(to_number, message):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_number
        )
        return True
    except Exception as e:
        print("SMS sending failed:", e)
        return False