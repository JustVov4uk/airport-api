from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airport.views import AirportViewSet, RouteViewSet

router = DefaultRouter()
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
app_name = "airport"