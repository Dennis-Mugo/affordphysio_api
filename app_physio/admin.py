from django.contrib import admin
from .models import PhysioUser, PhysioLog, PhysioSchedule, PostVisit
# Register your models here.

admin.site.register(PhysioUser)
admin.site.register(PhysioLog)
admin.site.register(PhysioSchedule)
admin.site.register(PostVisit)
