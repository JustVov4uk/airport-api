from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from airplane.models import Airplane
from airport.models import Route


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} -> {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    airplane = models.ForeignKey(Airplane, on_delete=models.PROTECT)
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        BOARDING = "boarding", "Boarding"
        DEPARTED = "departed", "Departed"
        ARRIVED = "arrived", "Arrived"
        CANCELLED = "cancelled", "Cancelled"
        DELAYED = "delayed", "Delayed"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    class Meta:
        verbose_name_plural = "flights"

    def __str__(self):
        return f"{self.route} -> {self.airplane}"

    def get_tickets_price(self):
        capacity = self.airplane.capacity
        sold = self.tickets.count()
        if capacity == 0:
            return self.base_price

        occupancy = sold / capacity


        if occupancy <= 0.5:
            return self.base_price * Decimal("1.0")
        if occupancy <= 0.8:
            return self.base_price * Decimal("1.25")
        else:
            return self.base_price * Decimal("1.5")

    def clean(self):
        if self.departure_time >= self.arrival_time:
            raise ValidationError("Departure time must be before arrival time")

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.clean()
        return super(Flight, self).save(
            force_insert, force_update, using, update_fields
        )
