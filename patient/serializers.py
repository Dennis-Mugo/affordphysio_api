from rest_framework import serializers
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
    class Meta:
        model = Appointment
        exclude = []


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
