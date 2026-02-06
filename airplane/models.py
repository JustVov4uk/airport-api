from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name_plural = "airplanes"

    def __str__(self):
        return f"{self.airplane_type} -> {self.name} ({self.rows}), ({self.seats_in_row})"
