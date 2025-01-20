import base64
import requests
from dotenv import load_dotenv
import os
load_dotenv()
import datetime

consumer_key = os.getenv('MPESA_CONSUMER_KEY')
consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
passkey = os.getenv('MPESA_PASS_KEY')

short_code = 174379

def encodeb64(txt):
    res = txt.encode("utf-8")
    # Base64 encode
    res = base64.b64encode(res)
    # Convert back to string
    res = res.decode("utf-8")
    return res


def get_access_token():
    res = requests.get(f'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', auth=(consumer_key, consumer_secret))
    access_token = res.json()['access_token']
    print(access_token)
    return access_token

def get_sandbox_token():
    response = requests.request("GET", 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', headers = {'Authorization': 'Basic ' + encodeb64(f'{consumer_key}:{consumer_secret}')})

    response = response.json()
    token = response['access_token']
    print(token)
    return token

def register_url():
    access_token = get_access_token()
    
    url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "ShortCode": short_code,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://affordphysio-api.onrender.com/patient/confirm_payment",
        "ValidationURL": "https://affordphysio-api.onrender.com/patient/validate_payment"
    }
    res = requests.post(url, json=payload, headers=headers)
    
    print(res.json())

def send_stk_push(phone_number, amount, account_reference="Afford Physio"):
    access_token = get_sandbox_token()
    print(access_token)
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"}
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    print(timestamp)
    password = f"{short_code}{passkey}{timestamp}"
    password = encodeb64(password)
    print(password)

    payload = {
        "BusinessShortCode": short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://affordphysio-api.onrender.com/patient/confirm_payment",
        "AccountReference": account_reference,
        "TransactionDesc": "Payment for services"
    }
    res = requests.post(url, json=payload, headers=headers)
    print(res)
    print(res.json())
    return res.json()

# send_stk_push(254742063263, 5)
# send_stk_push("254717811921", 1, "YESH")
# send_stk_push(254703961456, 1, "")


# register_url()
# get_access_token()
# get_sandbox_token()



failure = {
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "c62b-4e23-a479-5f74de8082a1203738",
            "CheckoutRequestID": "ws_CO_20012025115333444717811921",
            "ResultCode": 1032,
            "ResultDesc": "Request cancelled by user"
        }
    }
}


success = {
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "c62b-4e23-a479-5f74de8082a1203431",
            "CheckoutRequestID": "ws_CO_20012025114349982717811921",
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "CallbackMetadata": {
                "Item": [
                    {
                        "Name": "Amount",
                        "Value": 1.0
                    },
                    {
                        "Name": "MpesaReceiptNumber",
                        "Value": "TAK9UA2F5R"
                    },
                    {
                        "Name": "Balance"
                    },
                    {
                        "Name": "TransactionDate",
                        "Value": 20250120114400
                    },
                    {
                        "Name": "PhoneNumber",
                        "Value": 254717811921
                    }
                ]
            }
        }
    }
}







