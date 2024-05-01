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
        return self.first_name + " " + self.email
    

class PatientLog(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False),
    timestamp = models.DateTimeField(null=True)
    activity = models.CharField(null=True, max_length=50)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity
    
class PatientFeedback(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    timestamp = models.DateTimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # physiotherapist = models.ForeignKey()
    comments = models.TextField(null=True)
    rating = models.IntegerField(null=True)

    def __str__(self):
        return self.patient.email + " " + self.comments[:10]
    

class Appointment(models.Model):
    # id = models.UUIDField( 
    #      primary_key = True, 
    #      default = uuid.uuid4, 
    #      editable = False)
    timestamp = models.DateTimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # physiotherapist = models.ForeignKey()
    status = models.CharField(null=True, max_length=50)
    appointment_type = models.CharField(null=True, max_length=50)

    def __str__(self):
        return self.patient.first_name + " " + self.status


class AppointmentCancellation(models.Model):
    timestamp = models.DateTimeField(null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    reason = models.TextField(null=True)

    
