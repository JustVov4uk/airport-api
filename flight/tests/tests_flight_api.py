import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from flight.models import Flight
from flight.tests.helpers import create_route, create_airplane, create_flight, create_crew, create_airport
from order.models import Order, Ticket

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


class FlightFilterApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.source1 = create_airport(name="Kyiv")
        self.source2 = create_airport(name="London")
        self.destination1 = create_airport(name="Lviv")
        self.destination2 = create_airport(name="Paris")
        self.route1 = create_route(source=self.source1, destination=self.destination1)
        self.route2 = create_route(source=self.source2, destination=self.destination2)
        self.flight1 = create_flight(route=self.route1)
        self.flight2 = create_flight(route=self.route2)


    def test_filter_flights_by_route_source(self):
        result_request = self.client.get(FLIGHT_URL, {"route__source": self.route1.id})
        flight_ids = [item["id"] for item in result_request.data["results"]]
        self.assertNotIn(self.flight2.id, flight_ids)
        self.assertIn(self.flight1.id, flight_ids)

    def test_filter_flights_by_route_destination(self):
        result_request = self.client.get(FLIGHT_URL, {"route__destination": self.destination1.id})
        flight_ids = [item["id"] for item in result_request.data["results"]]
        self.assertNotIn(self.flight2.id, flight_ids)
        self.assertIn(self.flight1.id, flight_ids)

    def test_filter_flights_by_departure_date_from(self):
        past_flight = create_flight(
            departure_time=datetime.datetime(
                2025, 6, 1, 10, 0, tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2025, 6, 1, 12, 0, tzinfo=datetime.timezone.utc
            )
        )
        future_flight = create_flight(
            departure_time=datetime.datetime(
                2026, 6, 1, 10, 0, tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2026, 6, 1, 12, 0, tzinfo=datetime.timezone.utc
            )
        )
        result_request = self.client.get(FLIGHT_URL, {"departure_date_from": "2025-12-31"})
        ids = [item["id"] for item in result_request.data["results"]]
        self.assertIn(future_flight.id, ids)
        self.assertNotIn(past_flight.id, ids)

    def test_filter_flights_by_departure_date_to(self):
        past_flight = create_flight(
            departure_time=datetime.datetime(
                2025, 1, 1, 10, 0, tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2025, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
            )
        )
        future_flight = create_flight(
            departure_time=datetime.datetime(
                2025, 6, 1, 10, 0, tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2025, 6, 1, 12, 0, tzinfo=datetime.timezone.utc
            )
        )
        result_request = self.client.get(FLIGHT_URL, {"departure_date_to": "2025-02-01"})
        ids = [item["id"] for item in result_request.data["results"]]
        self.assertIn(past_flight.id, ids)
        self.assertNotIn(future_flight.id, ids)
        self.assertNotIn(self.flight1.id, ids)
        self.assertNotIn(self.flight2.id, ids)

    def test_filter_has_available_seats(self):
        full_airplane = create_airplane(rows=1, seats_in_row=1)
        full_flight = create_flight(airplane=full_airplane)
        user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        order = Order.objects.create(user=user)
        Ticket.objects.create(
            flight=full_flight,
            order=order,
            row=1,
            seat=1,
            price=100,
        )

        empty_flight = create_flight()

        result_request = self.client.get(FLIGHT_URL, {"has_available_seats": True})
        ids = [item["id"] for item in result_request.data["results"]]
        self.assertIn(empty_flight.id, ids)
        self.assertNotIn(full_flight.id, ids)


class FlightActionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.flight = create_flight()

    def test_available_seats_returns_list(self):
        url = reverse("flight:flight-available-seats", args=[self.flight.id])
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIsInstance(result.data, list)
        self.assertTrue(len(result.data) > 0)

    def test_available_seats_excludes_taken(self):
        user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        order = Order.objects.create(user=user)
        Ticket.objects.create(
            flight=self.flight,
            order=order,
            row=1,
            seat=1,
            price=100,
        )

        url = reverse("flight:flight-available-seats", args=[self.flight.id])
        result = self.client.get(url)
        self.assertNotIn({"row": 1, "seat": 1}, result.data)

    def test_occupancy_admin(self):
        admin = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
            is_staff=True,
        )
        self.client.force_authenticate(admin)

        airplane = create_airplane(rows=10, seats_in_row=1)
        flight = create_flight(airplane=airplane)
        user = get_user_model().objects.create_user(
            email="user@email",
            password="pass",
        )
        order = Order.objects.create(user=user)
        Ticket.objects.create(
            flight=flight,
            order=order,
            row=1,
            seat=1,
            price=100,
        )

        url = reverse("flight:flight-occupancy", args=[flight.id])
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["occupancy"], 10.0)

    def test_occupancy_forbidden_for_user(self):
        user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.client.force_authenticate(user)
        url = reverse("flight:flight-occupancy", args=[self.flight.id])
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
