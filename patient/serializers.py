from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude=['password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active']
