from rest_framework import serializers

from airplane.serializers import AirplaneListSerializer
from airport.serializers import RouteListSerializer
from flight.models import Crew, Flight


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
            "base_price",
            "status",
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "available_seats",
            "base_price",
            "status",
        )


class FlightDetailSerializer(FlightListSerializer):
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
            "available_seats",
            "base_price",
            "status",
        )


class FlightShortSerializer(FlightListSerializer):

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
        )
