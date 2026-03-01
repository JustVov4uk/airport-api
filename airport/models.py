from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)


    class Meta:
        verbose_name_plural = "airports"

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="routes_from")
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="routes_to")
    distance = models.PositiveIntegerField(validators=[MinValueValidator(1)])


    class Meta:
        verbose_name_plural = "routes"

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.distance})"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "Source is not destination"
            )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.clean()
        return super(Route, self).save(
            force_insert, force_update, using, update_fields
        )