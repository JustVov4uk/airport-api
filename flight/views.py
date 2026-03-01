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

    @extend_schema(
        summary="List all crew members",
        description="Get a paginated list of crew members with search by first or last name",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search by first name or last name",
                required=False,
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type",
            ).annotate(
                available_seats=ExpressionWrapper(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets"),
                    output_field=IntegerField()
                )
            )
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type"
            ).prefetch_related("crew")

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

    @extend_schema(
        summary="List all flights",
        description="""
        Get a paginated list of all flights with advanced filtering options.

        You can filter by:
        - Source and destination airport
        - Departure date range
        - Availability of seats

        Results are ordered by departure time by default.
        """,
        parameters=[
            OpenApiParameter(
                name="route__source",
                description="Filter flights by source airport ID",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="route__destination",
                description="Filter flights by destination airport ID",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="departure_date_from",
                description="Filter flights departing on or after this date (format: YYYY-MM-DD)",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="departure_date_to",
                description="Filter flights departing on or before this date (format: YYYY-MM-DD)",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="has_available_seats",
                description="Show only flights with available seats (True/False)",
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name="ordering",
                description="Order results by field. Prefix with '-' for descending order (e.g., '-departure_time')",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="page",
                description="Page number for pagination",
                required=False,
                type=int
            )
        ]
    )


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
