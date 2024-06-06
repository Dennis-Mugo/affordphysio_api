from django.contrib import admin
from .models import PhysioUser, PhysioLog
# Register your models here.

admin.site.register(PhysioUser)
admin.site.register(PhysioLog)
