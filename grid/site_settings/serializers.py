from rest_framework import serializers

from grid.site_settings.models import CompanySize, Country, State


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["uuid", "name", "two_letter_code", "country"]


class CompanySizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySize
        fields = ["uuid", "name"]
