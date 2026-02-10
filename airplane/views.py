from rest_framework import viewsets
from airplane.models import AirplaneType, Airplane
from airplane.serializers import AirplaneTypeSerializer, AirplaneSerializer
from config.permissions import IsAdminOrReadOnly


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)
