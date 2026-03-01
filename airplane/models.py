from django.core.validators import MinValueValidator
from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.PROTECT)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    class Meta:
        verbose_name_plural = "airplanes"

    def __str__(self):
        return f"{self.airplane_type} -> {self.name} ({self.rows}), ({self.seats_in_row})"
