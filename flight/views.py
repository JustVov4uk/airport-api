import django_filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from django.db.models import F, Count, ExpressionWrapper, IntegerField
from rest_framework import viewsets, filters
from rest_framework.response import Response

from config.permissions import IsAdminOrReadOnly
from flight.models import Crew, Flight
from flight.serializers import (CrewSerializer,
                                FlightSerializer,
                                FlightListSerializer,
                                FlightDetailSerializer
                                )
from order.models import Ticket


class FlightFilter(django_filters.FilterSet):
    departure_date_from = django_filters.DateFilter(
        field_name="departure_time",
        lookup_expr="gte"
    )
    departure_date_to = django_filters.DateFilter(
        field_name="departure_time",
        lookup_expr="lte"
    )
    has_available_seats = django_filters.BooleanFilter(method="filter_has_available_seats")

    class Meta:
        model = Flight
        fields = ["route__source", "route__destination"]

    def filter_has_available_seats(self, queryset, name, value):
        if value:
            return queryset.filter(available_seats__gt=0)
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ["first_name", "last_name"]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = FlightFilter
    ordering_fields = ["departure_time", "route__source__name"]
    ordering = ["departure_time"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("route", "airplane").annotate(
                available_seats = ExpressionWrapper(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("ticket"),
                    output_field=IntegerField()
                )
            )
        if self.action == "retrieve":
            queryset = queryset.select_related("route", "airplane")

        return queryset

    @extend_schema(
        summary="Get available seats",
        description="Return list of available seat coordinates",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "row": {"type": "integer"},
                        "seat": {"type": "integer"},
                    }
                }
            }
        }
    )



    @action(
        methods=["GET"],
        detail=True,
        url_path="available-seats",
    )
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        all_seats = []
        for row in range(1, flight.airplane.rows + 1):
            for seat in range(1, flight.airplane.seats_in_row + 1):
                all_seats.append({"row": row, "seat": seat})

        taken_seats = Ticket.objects.filter(flight=flight).values("row", "seat")
        taken_seats_set = {(seat["row"], seat["seat"]) for seat in taken_seats}
        available_sets = []
        for seat in all_seats:
            if (seat["row"], seat["seat"]) not in taken_seats_set:
                available_sets.append(seat)
        return Response(available_sets)
