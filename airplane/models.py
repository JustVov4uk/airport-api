import pathlib
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.name)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    )
    return pathlib.Path("upload/airplanes/") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.PROTECT)
    image = models.ImageField(null=True, upload_to=airplane_image_path)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    class Meta:
        verbose_name_plural = "airplanes"

    def __str__(self):
        return f"{self.airplane_type} -> {self.name} ({self.rows}), ({self.seats_in_row})"
