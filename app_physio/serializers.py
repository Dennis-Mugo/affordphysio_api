from rest_framework import serializers

from manager.app_serializers import ManagerSerializer
from physiotherapist.app_serializers import PhysioCategoriesSerializer
from .models import PhysioUser, PhysioLog, PhysioSchedule, PostVisit
from django.contrib.auth.models import User


class PhysioUserSerializer(serializers.ModelSerializer):
    created_by = ManagerSerializer(many=False, read_only=True)
    category = PhysioCategoriesSerializer(many=False, read_only=True)
    show_created_by = True

    class Meta:
        model = PhysioUser
        fields = ("id", "username", "email", "password", "first_name", "last_name", "created_date", "modified_date",
                  "created_by", "is_active", "last_login", "specialty", "pck_number", "phone_number", "gender",
                  "education", "years_of_experience", "description", "category","image")
        write_only_fields = ("password",)
        read_only_fields = ("id", "created_date", "modified_date",)

    def __init__(self, instance=None, show_created_by: bool = True, **kwargs):
        """
        Initialize serializer with arguments

        param: show_created_by: Influences if we are going to show `created_by` field
        """
        super().__init__(instance=instance, **kwargs)
        self.show_created_by = show_created_by

    def create(self, validated_data):
        physiotherapist: PhysioUser = PhysioUser.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            created_by=self.created_by
        )
        physiotherapist.set_password(validated_data["password"])
        physiotherapist.save()
        return physiotherapist

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("password", None)
        if not self.show_created_by:
            response.pop("created_by")
        return response


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
