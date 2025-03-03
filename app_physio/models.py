from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class PhysioUser(User):
    gender = models.CharField(max_length=50, null=True)
    id_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateTimeField(null=True)
    phone_number = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    years_of_experience = models.TextField(null=True)
    specialty = models.TextField(null=True)
    pck_number = models.IntegerField(null=True)
    clinic = models.CharField(max_length=50, null=True)
    home_address = models.TextField(null=True)

    def __str__(self):
        return str(self.id) + " " + self.first_name
    

class PhysioLog(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False),
    timestamp = models.DateTimeField(null=True)
    activity = models.CharField(null=True, max_length=50)
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity
    

class PhysioSchedule(models.Model):
    date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    appointment_type = models.CharField(null=True, max_length=50)
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + self.appointment_type
    
class PostVisit(models.Model):
    patient = models.IntegerField(null=False)
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    treatment_plan = models.TextField(null=False)
    recommendations = models.TextField(null=False)
    follow_up_date = models.DateField(null=False)
    pain_management = models.TextField(null=False)
    feedback = models.TextField(null=False)
    date_created = models.DateTimeField(auto_now_add=True)


class PhysioLocation(models.Model):
    physio = models.ForeignKey(PhysioUser, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Latitude: " + str(self.latitude) + ", Longitude: " + str(self.longitude)