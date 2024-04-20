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
        return self.first_name
    
class EmailToken(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    date_created = models.DateTimeField(auto_now_add=True)

    
    
    




