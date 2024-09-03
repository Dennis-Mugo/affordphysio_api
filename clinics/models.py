from datetime import datetime

import django.utils.timezone
from django.db import models

from app_physio.models import PhysioUser
from manager.models import Manager
from patient.models import Appointment


# Create your models here.

class Clinic(models.Model):
    name = models.CharField(max_length=1000)
    location_description = models.CharField(max_length=1000)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    image = models.ImageField(upload_to='assets/clinics/', null=False, blank=False)
    created_by = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True)
    open_time = models.TimeField(editable=True, null=False)
    close_time = models.TimeField(editable=True, null=False)


class PhysioClinic(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    physiotherapist = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)


class ClinicImages(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='assets/clinics/', null=False, blank=False)
    created_at = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified_at = models.DateTimeField(auto_now=True, editable=False)


class ClinicReviews(models.Model):
    user = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    rating = models.IntegerField(null=False)
    comment = models.TextField(null=False)
    visit_date = models.DateTimeField(null=False)
    visit_reason = models.TextField(null=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified_at = models.DateTimeField(auto_now=True, editable=False)