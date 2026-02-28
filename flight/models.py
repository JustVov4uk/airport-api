from decimal import Decimal

from django.db import models

from airplane.models import Airplane
from airport.models import Route


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} -> {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name_plural = "flights"

    def __str__(self):
        return f"{self.route} -> {self.airplane}"

    def get_tickets_price(self):
        capacity = self.airplane.capacity
        sold = self.ticket_set.count()
        if capacity == 0:
            return self.base_price

        occupancy = sold / capacity


        if occupancy <= 0.5:
            return self.base_price * Decimal("1.0")
        if occupancy <= 0.8:
            return self.base_price * Decimal("1.25")
        else:
            return self.base_price * Decimal("1.5")
