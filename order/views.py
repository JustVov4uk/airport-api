from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from order.models import Order, Ticket
from order.serializers import OrderSerializer, TicketSerializer, OrderListSerializer, TicketListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user_id=user.id)

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
