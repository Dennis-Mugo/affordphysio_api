from rest_framework import serializers
from .models import PhysioUser, PhysioLog, PhysioSchedule, PostVisit, PhysioLocation
from django.contrib.auth.models import User


class PhysioUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioUser
        # fields = ['id', 'email', 'password', 'first_name', 'last_name', 'username', 'gender', 'gender', 'phone_number', 'id_number', 'date_of_birth', 'education', 'years_of_experience']
        exclude=['password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active']

class PhysioLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioLog
        exclude = []

class PhysioScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioSchedule
        exclude = []

class PostVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVisit
        exclude = []

class PhysioLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioLocation
        exclude = []

