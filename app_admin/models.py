import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AppAdmin(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    

    def __str__(self):
        return self.full_name + " " + self.email
    
class AdminUser(User):
    gender = models.CharField(max_length=50, null=True)
    id_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateTimeField(null=True)
    phone_number = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    years_of_experience = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id) + " " + self.first_name
    
class EmailToken(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    date_created = models.DateTimeField(auto_now_add=True)

class ServiceProvided(models.Model):
    service_type = models.CharField(null=True, max_length=100)
    amount_charged = models.IntegerField(null=True)

class EducationResource(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    resource_type = models.CharField(null=True, max_length=50)
    url = models.CharField(null=True, max_length=100)

    
    
    




