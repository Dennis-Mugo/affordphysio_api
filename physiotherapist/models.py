import uuid

from django.db import models
from rest_framework.authtoken.admin import User

from manager.models import Manager



class PhysioPackages(models.Model):
    name = models.CharField(max_length=400, unique=True)
    description = models.TextField(max_length=2000, blank=False,
                                   null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class PhysiotherapistCategories(models.Model):
    name = models.CharField(max_length=400, unique=False)
    description = models.TextField(max_length=2000, blank=False,
                                   null=False)
    image = models.ImageField(upload_to="assets/physiotherapist_categories/", null=False, blank=True)


# Create your models here.
class Physiotherapist(User):
    created_by = models.ForeignKey(Manager, on_delete=models.RESTRICT, related_name="+")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(PhysiotherapistCategories, on_delete=models.SET_NULL, blank=True, null=True)
