import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Manager(AbstractUser):
    """
    An instance of a manager
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    email = models.EmailField()
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
