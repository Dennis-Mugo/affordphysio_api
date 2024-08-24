from rest_framework import serializers

from clinics.models import Clinic
from manager.app_serializers import ManagerSerializer


class ClinicsSerializer(serializers.ModelSerializer):
    created_by = ManagerSerializer(many=False, read_only=True)

    class Meta:
        model = Clinic
        exclude = []
