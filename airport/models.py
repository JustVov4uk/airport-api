from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)


class Route(models.Model):
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance = models.IntegerField()
