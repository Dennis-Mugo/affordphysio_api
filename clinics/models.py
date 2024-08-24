from datetime import datetime

import django.utils.timezone
from django.db import models

from manager.models import Manager


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
