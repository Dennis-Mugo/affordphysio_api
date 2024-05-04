from rest_framework import serializers
from .models import AppAdmin, AdminUser, EmailToken, ServiceProvided, EducationResource
from django.contrib.auth.models import User


class AppAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppAdmin
        fields = ['id', 'full_name', 'email']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'username']

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        # fields = ['id', 'email', 'password', 'first_name', 'last_name', 'username', 'gender', 'gender', 'phone_number', 'id_number', 'date_of_birth', 'education', 'years_of_experience']
        exclude=['password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active']

class EmailTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailToken
        fields = ['id', 'date_created']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvided
        exclude = []

class EdResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationResource
        exclude = []