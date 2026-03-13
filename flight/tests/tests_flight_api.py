from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from flight.models import Flight
from flight.tests.helpers import create_route, create_airplane, create_flight, create_crew

FLIGHT_URL = reverse("flight:flight-list")

def flight_detail_url(flight):
    return reverse("flight:flight-detail", args=[flight.id])

class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.flight = create_flight()

    def test_list_flights_anonymous(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_flight_anonymous(self):
        url = flight_detail_url(self.flight)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_flight_anonymous_forbidden(self):
        payload = {
            "route": create_route().id,
            "airplane": create_airplane().id,
            "departure_time": "2026-06-01T10:00:00Z",
            "arrival_time": "2026-06-01T12:00:00Z",
            "base_price": "100.00"
        }
        result_request = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_flight_authorized_forbidden(self):
        payload = {
            "route": create_route().id,
            "airplane": create_airplane().id,
            "departure_time": "2026-06-01T10:00:00Z",
            "arrival_time": "2026-06-01T12:00:00Z",
            "base_price": "100.00"
        }
        result_request = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.flight = create_flight()

    def test_create_flight_admin(self):
        payload = {
            "route": create_route().id,
            "airplane": create_airplane().id,
            "crew": [create_crew().id],
            "departure_time": "2026-06-01T10:00:00Z",
            "arrival_time": "2026-06-01T12:00:00Z",
            "base_price": "100.00"
        }
        flight_before = Flight.objects.count()
        result_request = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), flight_before + 1)

    def test_update_flight_admin(self):
        url = flight_detail_url(self.flight)
        payload = {
            "route": create_route().id,
            "airplane": create_airplane().id,
            "crew": [create_crew().id],
            "departure_time": "2026-06-01T10:00:00Z",
            "arrival_time": "2026-06-01T12:00:00Z",
            "base_price": "150.00"
        }
        result_request = self.client.put(url, payload)
        self.assertEqual(result_request.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.base_price, 150)

    def test_delete_flight_admin(self):
        url = flight_detail_url(self.flight)
        result_request = self.client.delete(url)
        self.assertEqual(result_request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flight.objects.filter(id=self.flight.id).exists())
