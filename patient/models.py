from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Patient(User):
    # patientId = models.UUIDField(
    #     primary_key = True, 
    #     default = uuid.uuid4, 
    #     editable = False
    # )
    id_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateTimeField(null=True)
    gender = models.CharField(max_length=50, null=True)
    weight = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    phone_number = models.CharField(max_length=15, null=True)
    marital_status = models.CharField(max_length=30, null=True)
    religion = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    chronic_disease_history = models.TextField(null=True)
    occupation = models.CharField(max_length=50, null=True)
    hobby = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.first_name

