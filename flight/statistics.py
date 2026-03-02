from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from flight.models import Flight
from order.models import Order, Ticket


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_view(request):
    total_flights = Flight.objects.all().count()
    total_orders = Order.objects.all().count()
    total_tickets = Ticket.objects.all().count()
    total_passengers = Order.objects.values("user").distinct().count()

    return Response ({
        "total_flights": total_flights,
        "total_orders": total_orders,
        "total_tickets": total_tickets,
        "total_passengers": total_passengers,
    })
