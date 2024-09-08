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