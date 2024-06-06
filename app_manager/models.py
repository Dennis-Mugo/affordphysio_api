import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

    
class ManagerUser(User):
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

class ManagerLog(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False),
    timestamp = models.DateTimeField(null=True)
    activity = models.CharField(null=True, max_length=50)
    manager = models.ForeignKey(ManagerUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity


    
    
    




