from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flight.views import CrewViewSet, FlightViewSet

router = DefaultRouter()
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
app_name = "flight"
