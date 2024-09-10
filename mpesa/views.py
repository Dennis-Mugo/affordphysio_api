import logging
from gc import callbacks

from django.shortcuts import render, resolve_url, get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import format_successful_operation
from manager.views import make_request
from mpesa.app_serializers import MpesaDepositErrorsSerializer, MpesaPaymentSerializer
from mpesa.models import MpesaPayment, Wallet, MpesaWithdrawal, MpesaDepositErrors, Deposit, MpesaCallBackResponse
from mpesa.utils import send_stk_push, verify_payment, mpesa_withdrawal, MpesaStatus
from patient.models import Patient


def format_error(errors, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "status": status_code,
        "errors": {"exception": [errors]},
        "data": None,
        "status_description": "Error occurred "
    }, headers={}, status=status_code)


# Create your views here.
def get_callback_url(request, reverse_name="mpesa_callback"):
    callback_url = resolve_url(reverse_name)
    callback_url = request.build_absolute_uri(callback_url)
    callback_url = callback_url.replace("http", "https")

    return callback_url


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def deposit_mpesa(request):
    def deposit_mpesa_inner(request):
        data = request.data
        user = request.user
        patient = Patient.objects.get(id=user.id)
        amount = data.get("amount")
        phone_number = patient.phone_number
        # ensure phone number and amount are not null
        if amount is None:
            return format_error("amount is required", status.HTTP_400_BAD_REQUEST)

        callback_url = get_callback_url(request, "mpesa_callback")
        # callback_url = "https://webhook.site/0f3983be-6d44-4cce-aab0-020281f6d504"
        response = send_stk_push(
            phone_number=phone_number, amount=int(amount), callback_url=callback_url
        )
        if response.status_code == 200:
            res = response.json()
            checkoutID = res["CheckoutRequestID"]
            merchantID = res["MerchantRequestID"]

            re = MpesaPayment.objects.create(
                user=patient,
                amount=float(amount),
                checkout_id=checkoutID,
                merchant_id=merchantID,
                response_code=res["ResponseCode"],
                response_description=res["ResponseDescription"],
                customer_message=res["CustomerMessage"],
                status=0,
            )
            re.save()
            serializer = MpesaPaymentSerializer(instance=re)

            response = {
                "status": status.HTTP_200_OK,
                "status_description": "Ok",
                "errors": None,
                "data": serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)

        if response.status_code == 400 or response.status_code == 500:
            json = response.json()
            error = MpesaDepositErrors.objects.create(user=patient, amount=float(amount),
                                                      request_id=json["requestId"],
                                                      error_code=json["errorCode"], error_msg=json["errorMessage"])
            error.save()
            error_serialized = MpesaDepositErrorsSerializer(
                instance=error
            )
            response = {
                "status": 400,
                "status_description": "Error Occurred",
                "data": None,
                "serialized_error": error_serialized.data
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response.json(), status=response.status_code)

    return make_request(request, deposit_mpesa_inner)


@api_view(["POST"])
def mpesa_callback(request):
    def mpesa_callback_inner(request):
        data = request.data["Body"]["stkCallback"]
        logging.error(data)
        result_code = 0
        if isinstance(data["ResultCode"], str):
            result_code = int(data["ResultCode"])
        if isinstance(data["ResultCode"], int):
            result_code = data["ResultCode"]

        result_description = data["ResultDesc"]
        # record the fields
        merchant_request = data["MerchantRequestID"]
        checkout_request = data["CheckoutRequestID"]
        ## Get payment
        mpesa_payment = MpesaPayment.objects.get(merchant_id=merchant_request, checkout_id=checkout_request)

        if result_code != 0:
            callback = MpesaCallBackResponse.objects.create(payment=mpesa_payment, result_code=result_code,
                                                            result_description=result_description, status=result_code,
                                                            amount=0, mpesa_receipt_number="NULL")
            callback.save()

        else:
            # successful request
            metadata = data["CallbackMetadata"]["Item"]
            # Recipient Number
            receipt_number = metadata[1]["Value"]
            # amount
            amount = metadata[0]["Value"]
            # transaction date
            transaction_date = metadata[3]["Value"]

            mpesa_payment.status = 1

            mpesa_payment.save()
            callback = MpesaCallBackResponse.objects.create(
                payment=mpesa_payment,
                result_code=result_code,
                result_description=result_description,
                transaction_date=transaction_date,
                amount=float(amount),
                status=result_code,
                mpesa_receipt_number=receipt_number,

            )
            callback.save()
            ## callback is okay,

        return Response(data={}, status=status.HTTP_200_OK)

    return make_request(request, mpesa_callback_inner)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def verify_mpesa_payment(request):
    data = request.data
    checkout_id = data.get("checkout_id")
    if checkout_id is None:
        return format_error("checkout_id is required", status.HTTP_400_BAD_REQUEST)

    mpesaPayment = get_object_or_404(MpesaPayment, checkout_id=checkout_id)
    try:
        Deposit.objects.get(reference_number=mpesaPayment.checkout_id)
        return format_error("The request is already completed")

    except Deposit.DoesNotExist:
        mpesa_status = verify_payment(checkout_id=checkout_id)
        if mpesa_status is MpesaStatus.Completed:
            return Response(
                {"detail": "Transaction is completed"}, status=status.HTTP_200_OK
            )
        elif mpesa_status is MpesaStatus.Pending:
            return format_error("The transaction is being processed", status.HTTP_425_TOO_EARLY)
        else:
            return format_error("Payment failed, try again.", status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_withdrawal(user, amount: float, reference_number, method: str = "mpesa"):
    MpesaWithdrawal.objects.create(
        user=user, amount=amount, reference_number=reference_number, method=method
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def withdraw(request):
    user = request.user
    patient = Patient.objects.get(id=user.id)
    data = request.data
    amount = data.get("amount")
    method = data.get("method", "mpesa")
    phone_number = patient.phone_number
    if amount is None:
        return format_error("amount is required", status.HTTP_400_BAD_REQUEST)
    wallet = Wallet.objects.filter(user=request.user).first()
    if wallet is None:
        return format_error("Wallet does not exist", status.HTTP_404_NOT_FOUND)
    if wallet.balance < float(amount):
        return format_error("Insufficient funds", status.HTTP_400_BAD_REQUEST)
    if method == "mpesa":
        if phone_number is None:
            return format_error("phone number is required", status.HTTP_400_BAD_REQUEST)
        # TODO: Change callback url
        callback_url = get_callback_url(request=request, reverse_name="queue-callback")

        response = mpesa_withdrawal(
            amount=int(amount), phone_number=phone_number, callback_url=callback_url
        )
        if response.status_code == 200:
            resp = response.json()
            conversation_id = resp["ConversationID"]
            orginator_conversation_id = resp["OriginatorConversationID"]

            MpesaWithdrawal.objects.create(
                user=request.user,
                amount=int(amount),
                conversation_id=conversation_id,
                originator_conversation_id=orginator_conversation_id,
            )
            return Response(response.json())
        else:
            return Response(response.json(), status=response.status_code)
    else:
        return Response({"error": "Method is not currently supported"})


@api_view(["POST"])
def queue_callback(request):
    # print(request.body)
    data = request.data["Result"]
    result_code = data["ResultCode"]
    if result_code != 0:
        pass
    else:
        transaction_id = data["TransactionID"]
        conversation_id = data["ConversationID"]
        parameters = data["ResultParameters"]["ResultParameter"]
        amount = parameters[0]["Value"]
        mpesa_withdrawal = MpesaWithdrawal.objects.get(conversation_id=conversation_id)
        mpesa_withdrawal.reference_number = transaction_id
        mpesa_withdrawal.completed = True
        mpesa_withdrawal.save()
        create_withdrawal(
            user=mpesa_withdrawal.user,
            amount=int(amount),
            reference_number=mpesa_withdrawal.reference_number,
        )
    return Response({})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def get_mpesa_transactions(request):
    def get_mpesa_transactions_inner(request):
        user = request.user
        patient = Patient.objects.get(id=user.id)

        details = MpesaPayment.objects.filter(user=patient).order_by('-created_at')
        serializer = MpesaPaymentSerializer(details, many=True)

        return format_successful_operation(serializer.data)

    # return get_mpesa_transactions_inner(request)
    return make_request(request, get_mpesa_transactions_inner)
