import uuid

from django.db import models
from rest_framework.authtoken.admin import User


# Create your models here.

class Manager(User):
    """
    An instance of a manager
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
