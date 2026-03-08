from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from airplane.models import Airplane, AirplaneType
from rest_framework.reverse import reverse

AIRPLANE_URL = reverse("airplane:airplane-list")

def airplane_detail_url(airplane):
    return reverse("airplane:airplane-detail", args=[airplane.id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(name="Airbus")
        self.airplane = Airplane.objects.create(
            name="A320",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

    def test_list_airplanes_anonymous(self):
        result = self.client.get(AIRPLANE_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_airplane_anonymous(self):
        url = airplane_detail_url(self.airplane)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_airplane_anonymous_forbidden(self):
        payload = {
            "name": "A320",
            "rows": 25,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        result_request = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(name="Airbus")

    def test_create_airplane_authenticated_forbidden(self):
        payload = {
            "name": "A320",
            "rows": 25,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        result_request = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_403_FORBIDDEN)


