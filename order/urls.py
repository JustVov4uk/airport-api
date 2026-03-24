from django.urls import include, path
from rest_framework.routers import DefaultRouter

from order.views import OrderViewSet, TicketViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
app_name = "order"
