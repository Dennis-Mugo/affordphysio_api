from rest_framework import serializers
from .models import Patient, PatientLog, PatientFeedback, Appointment

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude=['password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active']


class PatientLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientLog
        exclude = []

class PatientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFeedback
        exclude = []

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        exclude = []