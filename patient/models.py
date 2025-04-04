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
    phone_number = models.CharField(max_length=15, null=True)
    marital_status = models.CharField(max_length=30, null=True)
    religion = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    occupation = models.CharField(max_length=50, null=True)
    chronic_disease_history = models.TextField(null=True)
    hobby = models.CharField(max_length=50, null=True)
    home_address = models.TextField(null=True)

    def __str__(self):
        return str(self.id) + " " + self.email
    

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
    timestamp = models.DateTimeField(null=True)
    end_time = models.TimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physiotherapist = models.ForeignKey(PhysioUser, on_delete=models.CASCADE, default=24)
    status = models.CharField(null=True, max_length=50)
    appointment_type = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " " + self.patient.first_name + " " + self.status

class Penalty(models.Model):
    penalty_type = models.CharField(null=True, max_length=50)
    fine_percentage = models.IntegerField(null=True)
    duration = models.BigIntegerField(null=True)
    #Duration in seconds before the appointment/duration in seconds that the physio is late

class AppointmentCancellation(models.Model):
    timestamp = models.DateTimeField(null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    reason = models.TextField(null=True)
    penalty = models.ForeignKey(Penalty, on_delete=models.CASCADE, null=True)

class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class MPesaPayment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    amount = models.FloatField(null=True)
    phone_number = models.CharField(max_length=15, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, null=True)
    status_message = models.CharField(max_length=50, null=True)
    request_id = models.CharField(max_length=50, null=True)
    checkout_id = models.CharField(max_length=50, null=True)


    def __str__(self):
        return self.patient.email + " " + str(self.amount)


class PatientLocation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Latitude: " + str(self.latitude) + ", Longitude: " + str(self.longitude)
    

class VideoRecommendation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    appointment= models.ForeignKey(Appointment, on_delete=models.CASCADE)
    video_url = models.TextField(null=False)
    category = models.CharField(max_length=50, null=True)
    is_done = models.BooleanField(default=False)
    patient_comments = models.TextField(null=True, default="")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category + " " + self.video_url[:10] + "id: " + str(self.id)
    

class PatientSymptom(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    symptoms = models.TextField(null=True)
    duration = models.CharField(max_length=100, null=True)
    type_of_pain = models.CharField(max_length=100, null=True)
    pain_intensity = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symptoms[:10] + " " + self.duration + " " + self.type_of_pain + " " + self.pain_intensity






    
