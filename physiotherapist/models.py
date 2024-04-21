from django.db import models
from rest_framework.authtoken.admin import User

from manager.models import Manager


# Create your models here.
class Physiotherapy(User):
    created_by = models.ForeignKey(Manager, related_name="+")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
