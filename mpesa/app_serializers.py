from rest_framework import serializers
from mpesa.models import MpesaDepositErrors, MpesaPayment, MpesaCallBackResponse, Wallet


class MpesaDepositErrorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaDepositErrors
        exclude = []


class MpesaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        exclude = ["user"]


class MpesaCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaCallBackResponse
        exclude = ["payment"]


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        exclude = []
