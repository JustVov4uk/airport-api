import django_filters
from django.db.models import F, Count, ExpressionWrapper, IntegerField
from rest_framework import viewsets, filters
from config.permissions import IsAdminOrReadOnly
from flight.models import Crew, Flight
from flight.serializers import (CrewSerializer,
                                FlightSerializer,
                                FlightListSerializer,
                                FlightDetailSerializer
                                )


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
