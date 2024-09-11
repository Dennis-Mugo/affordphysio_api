from rest_framework import serializers
from mpesa.models import MpesaDepositErrors, MpesaPayment, MpesaCallBackResponse


class MpesaDepositErrorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaDepositErrors
        exclude = []

class MpesaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        exclude = []

class MpesaCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaCallBackResponse
        exclude = []