from django.test import TestCase

from airplane.models import Airplane, AirplaneType


class AirplaneModelTest(TestCase):
    def setUp(self):
        self.airplane_type = AirplaneType.objects.create(name="Airbus")
        self.airplane = Airplane.objects.create(
            name="A320",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

    def test_capacity(self):
        self.capacity = self.airplane.rows * self.airplane.seats_in_row

        self.assertEqual(self.airplane.capacity, self.capacity)
