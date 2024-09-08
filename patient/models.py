from django.db import models
from django.contrib.auth.models import User
import uuid
from app_physio.models import PhysioUser


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
    phone_number = models.CharField(max_length=15, null=False)
    marital_status = models.CharField(max_length=30, null=True)
    religion = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    occupation = models.CharField(max_length=50, null=True)
    chronic_disease_history = models.TextField(null=True)
    hobby = models.CharField(max_length=50, null=True)
    image = models.ImageField(null=True,upload_to="assets/patient_images/")

    def __str__(self):
        return str(self.id) + " " + self.email


class PatientLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False),
    timestamp = models.DateTimeField(null=True)
    activity = models.CharField(null=True, max_length=50)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity


class PatientFeedback(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    timestamp = models.DateTimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physiotherapist = models.ForeignKey(PhysioUser, on_delete=models.CASCADE, default=24)
    comments = models.TextField(null=True)
    rating = models.IntegerField(null=True)

    def __str__(self):
        return self.patient.email + " " + self.comments[:10]


class Appointment(models.Model):
    # id = models.UUIDField( 
    #      primary_key = True, 
    #      default = uuid.uuid4, 
    #      editable = False)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physiotherapist = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    status = models.CharField(null=False, max_length=50)
    appointment_type = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    amount = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.patient.first_name + " " + self.status


class Penalty(models.Model):
    penalty_type = models.CharField(null=True, max_length=50)
    fine_percentage = models.IntegerField(null=True)
    duration = models.BigIntegerField(null=True)
    # Duration in seconds before the appointment/duration in seconds that the physio is late


class AppointmentCancellation(models.Model):
    timestamp = models.DateTimeField(null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    reason = models.TextField(null=True)
    penalty = models.ForeignKey(Penalty, on_delete=models.CASCADE, null=True)


class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
