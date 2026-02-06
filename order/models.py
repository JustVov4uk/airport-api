from django.conf import settings
from django.db import models

from flight.models import Flight



class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "orders"

    def __str__(self):
        return f"{self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "tickets"
        unique_together = ("flight", "row", "seat")
        ordering = ("seat",)

    def __str__(self):
        return f"{self.row}-{self.seat}"
