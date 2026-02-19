from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        verbose_name_plural = "tickets"
        unique_together = ("flight", "row", "seat")
        ordering = ("seat",)

    def __str__(self):
        return f"{self.row}-{self.seat}"

    @staticmethod
    def validate_ticket_field(value: int, max_value: int, field_name: str, error_to_raise):
        if not (1 <= value <= max_value):
            raise error_to_raise(
                {field_name: f"{field_name} must be in range [1, {max_value}], not {value}"}
            )

    def clean(self):
        Ticket.validate_ticket_field(self.seat, self.flight.airplane.seats_in_row, "seat", ValidationError)
        Ticket.validate_ticket_field(self.row, self.flight.airplane.rows, "row", ValidationError)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )
