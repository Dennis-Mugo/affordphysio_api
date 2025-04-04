from django.contrib import admin
from .models import Patient, PatientLog, PatientFeedback, Appointment, AppointmentCancellation, Penalty, Payment, PatientLocation, MPesaPayment, VideoRecommendation, PatientSymptom
# Register your models here.

admin.site.register(Patient)
admin.site.register(PatientLog)
admin.site.register(PatientFeedback)
admin.site.register(Appointment)
admin.site.register(AppointmentCancellation)
admin.site.register(Penalty)
admin.site.register(Payment)
admin.site.register(PatientLocation)
admin.site.register(MPesaPayment)
admin.site.register(VideoRecommendation)
admin.site.register(PatientSymptom)

