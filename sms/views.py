import codecs
import logging

import requests
from django.http import HttpRequest
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view

from manager.views import make_request
from mpesa.views import get_callback_url
from sms.models import Sms, SmsErrors, SmsDlr


def create_message(request,phone_number: str, message: str):
    # Don't put api keys in production (CAE),
    # Then goes to ignore that information
    key = "5o5398qr65q1388oq5q8n7r8q2p1269o"
    actual_key = codecs.decode(key, 'rot13')
    callback_url = get_callback_url(request, "mpesa_callback")

    url = "https://api.vaspro.co.ke/v3/BulkSMS/api/create"
    post_fields = {
        "apiKey": actual_key,
        "shortCode": "VasPro",
        "message": message,
        "recipient": phone_number,
        "callbackURL": callback_url,
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


@api_view(['POST'])
def sms_dlr(request):
    def sms_dlr_internal(req: HttpRequest):
        data = request.data
        api_data = SmsDlr(
            recipient=data['recepient'],
            correlator=data['correlator'],
            timestamp=parse_datetime(data['timestamp']),
            product_id=data['productId'],
            campaign_id=data['campaignId'],
            unique_id=data['uniqueId'],
            reference_id=data['referenceId'],
            billing_type=data['billing_type'],
            delivery_state=data['deliveryState'],
            delivery_status=data['deliveryStatus']
        )
        api_data.save()
    try:
        sms_dlr_internal(request)
    except Exception as e:
        logging.log("")