import codecs

import requests

from sms.models import Sms, SmsErrors


def create_message(phone_number: str, message: str):
    # Don't put api keys in production (CAE),
    # Then goes to ignore that information
    key = "5o5398qr65q1388oq5q8n7r8q2p1269o"
    actual_key = codecs.decode(key, 'rot13')
    url = "https://api.vaspro.co.ke/v3/BulkSMS/api/create"
    post_fields = {
        "apiKey": actual_key,
        "shortCode": "VasPro",
        "message": message,
        "recipient": phone_number,
        "callbackURL": "",
        "enqueue": 0
    }
    try:
        response = requests.post(url, json=post_fields, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        if response.status_code == 200:
            sms = Sms.objects.create(phone_number=phone_number, message=message, status=0)
            sms.save()
    except Exception as e:
        error = SmsErrors.objects.create(phone_number=phone_number, message=message, reason=str(e), status=0)
        error.save()
