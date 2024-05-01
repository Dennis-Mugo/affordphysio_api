from django.db import models
from rest_framework.authtoken.admin import User

from manager.models import Manager


# Create your models here.
class Physiotherapist(User):
    created_by = models.ForeignKey(Manager, on_delete=models.RESTRICT, related_name="+")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
