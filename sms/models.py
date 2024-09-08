from django.db import models


# Create your models here.
class Sms(models.Model):
    message = models.TextField()
    phone_number = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    arrived_at = models.DateTimeField(auto_now=True)


class SmsErrors(models.Model):
    message = models.TextField()
    phone_number = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()


class SmsDlr(models.Model):
    recipient = models.CharField(max_length=20)
    correlator = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    product_id = models.CharField(max_length=100)
    campaign_id = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=100)
    billing_type = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)
    delivery_status = models.CharField(max_length=100)
