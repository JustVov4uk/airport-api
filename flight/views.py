from rest_framework import viewsets

from config.permissions import IsAdminOrReadOnly
from flight.models import Crew, Flight
from flight.serializers import CrewSerializer, FlightSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrReadOnly,)
