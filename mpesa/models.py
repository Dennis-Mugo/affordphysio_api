from django.db import models
from django.db.models import ForeignKey

from patient.models import Patient


# Create your models here.

class MpesaPayment(models.Model):
    user = ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_id = models.CharField(max_length=256, unique=True)
    merchant_id = models.CharField(max_length=256, unique=True)
    response_code = models.CharField(max_length=256)
    response_description = models.CharField(max_length=256)
    customer_message = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)


class Deposit(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=256)
    method = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Wallet(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class MpesaWithdrawal(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    conversion_id = models.CharField(max_length=256)
    originator_conversion_id = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class MpesaDepositErrors(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_id = models.CharField(max_length=256)
    error_code = models.CharField(max_length=256)
    error_msg = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class MpesaCallBackResponse(models.Model):
    payment = models.ForeignKey(MpesaPayment, on_delete=models.CASCADE)
    result_code = models.CharField(max_length=256)
    result_description = models.CharField(max_length=256)
    mpesa_recipient_number = models.CharField(max_length=256, null=True, blank=True),
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
