from django.db import transaction
from rest_framework import serializers

from flight.serializers import FlightShortSerializer
from order.models import Order, Ticket
from user.serializers import UserSerializer


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order", "price")
        read_only_fields = ("order", "price")

    def validate(self, attrs):
        flight = attrs.get("flight")
        Ticket.validate_ticket_field(
            attrs["seat"],
            flight.airplane.seats_in_row,
            "seat",
            serializers.ValidationError
        )
        Ticket.validate_ticket_field(
            attrs["row"],
            flight.airplane.rows,
            "row",
            serializers.ValidationError
        )
        return attrs


class TicketListSerializer(serializers.ModelSerializer):
    flight = FlightShortSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "order",
            "price",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                flight = ticket_data["flight"]
                price = flight.get_tickets_price()
                Ticket.objects.create(order=order, price=price, **ticket_data)
            return order


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user",
            "tickets"
        )
