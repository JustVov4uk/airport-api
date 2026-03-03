from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, filters
from airport.models import Airport, Route
from config.permissions import IsAdminOrReadOnly
from airport.serializers import AirportSerializer, RouteSerializer, RouteListSerializer, AirportListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "city__name")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AirportListSerializer
        return AirportSerializer

    def get_queryset(self):
        return Airport.objects.select_related("city__country")


    
    @extend_schema(
        summary="List all airports",
        description="Get a paginated list of all airports with search by name or closest_big_city",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search airports by name or closest_big_city",
                required=False,
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        return Route.objects.select_related(
            "source__city__country",
            "destination__city__country",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer
