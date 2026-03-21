from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import Airport, City, Country

AIRPORT_URL = reverse("airport:airport-list")


def airport_detail_url(airport):
    return reverse("airport:airport-detail", args=[airport.id])


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = Country.objects.create(name="Ukraine")
        self.city = City.objects.create(name="Kyiv", country=self.country)
        self.airport = Airport.objects.create(name="Boryspil", city=self.city)

    def test_list_airports_anonymous(self):
        result = self.client.get(AIRPORT_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_airport_anonymous(self):
        url = airport_detail_url(self.airport)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_airport_anonymous_forbidden(self):
        payload = {
            "name": "Kyiv",
            "city": self.city.id,
        }
        result_request = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)
        self.country = Country.objects.create(name="Ukraine")
        self.city = City.objects.create(name="Kyiv", country=self.country)
        self.airport = Airport.objects.create(name="Boryspil", city=self.city)

    def test_list_airports_authenticated(self):
        result = self.client.get(AIRPORT_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_airport_authenticated(self):
        url = airport_detail_url(self.airport)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_airport_authenticated_forbidden(self):
        payload = {
            "name": "Kyiv",
            "city": self.city.id,
        }
        result_request = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.country = Country.objects.create(name="Ukraine")
        self.city = City.objects.create(name="Kyiv", country=self.country)
        self.airport = Airport.objects.create(
            name="Boryspil",
            city=self.city,
        )

    def test_list_airports_admin(self):
        result = self.client.get(AIRPORT_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_airport_admin(self):
        url = airport_detail_url(self.airport)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_airport_admin(self):
        payload = {
            "name": "Kyiv",
            "city": self.city.id,
        }
        airports_before = Airport.objects.count()
        result_request = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airports_before + 1, Airport.objects.count())

    def test_update_airport_admin(self):
        url = airport_detail_url(self.airport)
        payload = {
            "name": "London",
            "city": self.city.id,
        }
        result_request = self.client.put(url, payload)
        self.assertEqual(result_request.status_code, status.HTTP_200_OK)
        self.airport.refresh_from_db()
        self.assertEqual(self.airport.name, "London")
        self.assertEqual(self.airport.city, self.city)

    def test_delete_airport_admin(self):
        url = airport_detail_url(self.airport)
        result_request = self.client.delete(url)
        self.assertEqual(result_request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airport.objects.filter(id=self.airport.id).exists())
