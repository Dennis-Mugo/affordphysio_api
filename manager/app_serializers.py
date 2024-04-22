from rest_framework import serializers

from manager.models import Manager
from physiotherapist.models import Physiotherapist


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ("id", "username", "email", "password", "first_name", "last_name", "created_date", "modified_date")
        write_only_fields = ("password",)
        read_only_fields = ("id", "created_date", "modified_date",)

    def create(self, validated_data):
        user = Manager.objects.create(
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


class PhysioSerializer(serializers.ModelSerializer):
    created_by = ManagerSerializer(many=False, read_only=True)

    class Meta:
        model = Physiotherapist
        fields = ("id", "username", "email", "password", "first_name", "last_name", "created_date", "modified_date",
                  "created_by")
        write_only_fields = ("password",)
        read_only_fields = ("id", "created_date", "modified_date",)

    def create(self, validated_data):
        physiotherapist: Physiotherapist = Physiotherapist.objects.create(
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
        return response
