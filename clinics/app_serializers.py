from rest_framework import serializers

from clinics.models import Clinic, PhysioClinic, ClinicImages, ClinicReviews
from manager.app_serializers import ManagerSerializer


class ClinicsSerializer(serializers.ModelSerializer):
    created_by = ManagerSerializer(many=False, read_only=True)

    class Meta:
        model = Clinic
        exclude = []


class PhysioClinicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioClinic
        exclude = []

class ClinicImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicImages
        exclude = []


class ClinicReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicReviews
        exclude = []