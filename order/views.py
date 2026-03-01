from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.email import send_order_confirmation
from order.models import Order, Ticket
from order.serializers import (OrderSerializer,
                               TicketSerializer,
                               OrderListSerializer,
                               TicketListSerializer)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user_id=user.id)

    @extend_schema(
        summary="Cancel order",
        description="Cancel this order and delete all associated tickets. Only the order owner can cancel their order.",
        request=None,
        responses={
            204: None,
        }
    )

    @action(
        detail=True,
        methods=["POST"],
        url_path="cancel"
    )
    def cancel(self, request, pk=None):
        order = self.get_object()
        earliest_ticket = order.tickets.select_related("flight").order_by("flight__departure_time").first()
        if not earliest_ticket:
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        earliest_flight = earliest_ticket.flight

        if earliest_flight.departure_time - timezone.now() < timedelta(hours=24):
            return Response(
                {"error": "Cannot cancel order less than 24 hours before departure"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Create new order",
        description="Create a new order with tickets. Provide flight ID, row, and seat for each ticket.",
        request={
            "application/json":{
                "example":{
                    "tickets":[
                        {
                            "flight": 1,
                            "row": 5,
                            "seat": 2
                        },
                        {
                            "flight": 1,
                            "row": 5,
                            "seat": 3
                        }
                    ]
                }
            }
        },
        responses={
            201: OrderListSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        send_order_confirmation(order)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderListSerializer
        return OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(order__user=user.id)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TicketListSerializer
        return TicketSerializer
