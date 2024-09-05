from django.db import models
from django.contrib.auth.models import User
import uuid

from manager.models import Manager
from physiotherapist.models import PhysiotherapistCategories


# Create your models here.
class PhysioUser(User):
    created_by = models.ForeignKey(Manager, on_delete=models.RESTRICT, related_name="+")
    gender = models.CharField(max_length=50, null=True)
    id_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateTimeField(null=True)
    phone_number = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    years_of_experience = models.IntegerField(null=True)
    specialty = models.TextField(null=True)
    pck_number = models.IntegerField(null=True)
    description = models.TextField(null=False, default="")
    category = models.ForeignKey(PhysiotherapistCategories, on_delete=models.SET_NULL, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True,upload_to="assets/patient_images/")


    def __str__(self):
        return str(self.id) + " " + self.first_name


class PhysioLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False),
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
