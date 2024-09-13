from rest_framework import serializers

from physiotherapist.models import PhysioPackages, PhysiotherapistCategories


class PhysioCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysiotherapistCategories
        fields = '__all__'


class PhysioPackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysioPackages
        exclude = []
