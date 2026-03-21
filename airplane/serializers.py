from rest_framework import serializers

from airplane.models import Airplane, AirplaneType


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity"
        )


class AirplaneImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
        )
        read_only_fields = ("capacity",)
