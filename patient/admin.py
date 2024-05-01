from django.contrib import admin
from .models import Patient, PatientLog, PatientFeedback, Appointment, AppointmentCancellation
# Register your models here.

admin.site.register(Patient)
admin.site.register(PatientLog)
admin.site.register(PatientFeedback)
admin.site.register(Appointment)
admin.site.register(AppointmentCancellation)

