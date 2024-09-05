from rest_framework import serializers

from app_physio.serializers import PhysioUserSerializer
from clinics.models import Clinic, PhysioClinic, ClinicImages, ClinicReviews
from manager.app_serializers import ManagerSerializer
from patient.serializers import PatientSerializer


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
    user = PatientSerializer(many=False, read_only=True)

    class Meta:
        model = ClinicReviews
        exclude = []

    def create(self, validated_data):
        clinic_review: ClinicReviews = ClinicReviews.objects.create(
            clinic=validated_data['clinic'],
            visit_date=validated_data['visit_date'],
            visit_reason=validated_data['visit_reason'],
            comment=validated_data['comment'],
            rating=validated_data['rating'],
            user_id=self.user.id,

        )
        clinic_review.save()
        return clinic_review
