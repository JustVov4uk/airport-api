from rest_framework import serializers

from flight.serializers import FlightShortSerializer
from order.models import Order, Ticket
from user.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketListSerializer(serializers.ModelSerializer):
    flight = FlightShortSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "order"
        )


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user",
            "tickets"
        )
