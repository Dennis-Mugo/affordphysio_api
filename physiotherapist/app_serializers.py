from rest_framework import serializers

from physiotherapist.models import PhysiotherapistCategories


class PhysioCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysiotherapistCategories
        fields = '__all__'
