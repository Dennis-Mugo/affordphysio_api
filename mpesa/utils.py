from django_daraja.mpesa.utils import mpesa_config, mpesa_access_token
from datetime import datetime
import base64

from enum import Enum
from django_daraja.mpesa.core import MpesaClient

import requests


class MpesaStatus(Enum):
    Pending = "Pending"
    Failed = "Failed"
    Canceled = "Canceled"
    Completed = "Completed"
    Invalid = "Invalid"


class MpesaUtils:
    @classmethod
    def get_password(cls):
        passkey = mpesa_config("MPESA_PASSKEY")
        mpesa_environment = mpesa_config("MPESA_ENVIRONMENT")
        if mpesa_environment == "sandbox":
            business_short_code = mpesa_config("MPESA_EXPRESS_SHORTCODE")
        else:
            business_short_code = mpesa_config("MPESA_SHORTCODE")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (business_short_code + passkey + timestamp).encode("ascii")
        ).decode("utf-8")
        return password

    @classmethod
    def short_code(cls):
        mpesa_environment = mpesa_config("MPESA_ENVIRONMENT")
        if mpesa_environment == "sandbox":
            business_short_code = mpesa_config("MPESA_EXPRESS_SHORTCODE")
        else:
            business_short_code = mpesa_config("MPESA_SHORTCODE")
        return business_short_code

    @classmethod
    def timestamp(cls):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    @classmethod
    def access_token(cls) -> str:
        return mpesa_access_token()


def send_stk_push(phone_number: str, amount: int, *args, **kwargs):
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = phone_number
    amount = amount
    account_reference = kwargs.get("reference", "N2")
    transaction_desc = kwargs.get("description", "N2 Deposit")
    callback_url = kwargs.get(
        "callback_url", "https://api.darajambili.com/express-payment"
    )
    cl = MpesaClient()

    response = cl.stk_push(
        phone_number, amount, account_reference, transaction_desc, callback_url
    )
    return response


def verify_payment(checkout_id) -> MpesaStatus:
    # TODO: Change in production
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    password = MpesaUtils.get_password()
    short_code = MpesaUtils.short_code()
    timestamp = MpesaUtils.timestamp()
    checkout_request_id = checkout_id

    payload = {
        "BusinessShortCode": short_code,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }
    headers = {
        "Authorization": "Bearer " + MpesaUtils.access_token(),
        "Content-type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    resp = response.json()
    print(resp)
    if response.status_code == 200:
        result_code = resp["ResultCode"]
        if result_code == "0":
            return MpesaStatus.Completed
        elif result_code == "2001":
            return MpesaStatus.Invalid
        elif result_code == "1032":
            return MpesaStatus.Canceled
    elif resp["errorMessage"] == "The transaction is being processed":
        return MpesaStatus.Pending
    else:
        return MpesaStatus.Failed


def mpesa_withdrawal(phone_number, amount, *args, **kwargs):
    cl = MpesaClient()

    response = cl.b2c_payment(
        phone_number=phone_number,
        amount=amount,
        callback_url=kwargs.get(
            "callback_url", "https://api.darajambili.com/express-payment"
        ),
        transaction_desc=kwargs.get("description", "N2 Withdrawal"),
        occassion=kwargs.get("occassion"),
        command_id="PromotionPayment",
    )
    return response
