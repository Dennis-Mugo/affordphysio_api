from django.contrib import admin
from .models import Patient, PatientLog, PatientFeedback, Appointment
# Register your models here.

admin.site.register(Patient)
admin.site.register(PatientLog)
admin.site.register(PatientFeedback)
admin.site.register(Appointment)

