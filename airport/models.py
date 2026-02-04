from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)


    class Meta:
        verbose_name_plural = "airports"

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance = models.IntegerField()


    class Meta:
        verbose_name_plural = "routes"

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.distance})"
