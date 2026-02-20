import django_filters
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
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

    class Meta:
        model = Flight
        fields = ["route__source", "route__destination"]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = FlightFilter


    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
