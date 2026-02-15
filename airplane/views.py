from rest_framework import viewsets
from airplane.models import AirplaneType, Airplane
from airplane.serializers import AirplaneTypeSerializer, AirplaneSerializer, AirplaneListSerializer
from config.permissions import IsAdminOrReadOnly


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer
