from rest_framework import serializers

from app_physio.serializers import PhysioUserSerializer
from .models import Patient, PatientLog, PatientFeedback, Appointment, AppointmentCancellation, Penalty, Payment


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "username", "email", "password", "first_name", "last_name")
        write_only_fields = ("password",)
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = Patient.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("password", None)
        return response


class PatientLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientLog
        exclude = []


class PatientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFeedback
        exclude = []


class AppointmentSerializer(serializers.ModelSerializer):
    physiotherapist = PhysioUserSerializer(many=False, read_only=True, show_created_by=False)

    class Meta:
        model = Appointment
        exclude = []

    def create(self, validated_data):
        user = Appointment.objects.create(
            status=validated_data["status"],
            appointment_type=validated_data["appointment_type"],
            patient=validated_data["patient"],
            physiotherapist_id=self.physiotherapist.id,
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
        )

        user.save()
        return user


class AppointmentCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentCancellation
        exclude = []


class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        exclude = []


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = []
