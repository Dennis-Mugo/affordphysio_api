from django.contrib import admin
from .models import PhysioUser, PhysioLog, PhysioSchedule
# Register your models here.

admin.site.register(PhysioUser)
admin.site.register(PhysioLog)
admin.site.register(PhysioSchedule)
