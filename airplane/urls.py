from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airplane.views import AirplaneTypeViewSet, AirplaneViewSet


router = DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
app_name = "airplane"
