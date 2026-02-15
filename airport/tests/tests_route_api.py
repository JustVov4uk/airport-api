from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from airport.models import Route, Airport

ROUTE_URL = reverse("airport:route-list")

def route_detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airport = Airport.objects.create(
            name="Kyiv",
            closest_big_city="Lviv",
        )
        self.destination = Airport.objects.create(
            name="Lviv",
            closest_big_city="Kyiv",
        )
        self.route = Route.objects.create(
            source=self.airport,
            destination=self.destination,
            distance=600
        )

    def test_list_routes_anonymous(self):
        result = self.client.get(ROUTE_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_route_anonymous(self):
        url = route_detail_url(self.route)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_route_anonymous_forbidden(self):
        payload = {
            "source":self.airport.id,
            "destination":self.destination.id,
            "distance":600
        }
        result_request = self.client.post(ROUTE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="PASSWORD"
        )
        self.client.force_authenticate(user=self.user)
        self.airport = Airport.objects.create(
            name="Kyiv",
            closest_big_city="Lviv",
        )
        self.destination = Airport.objects.create(
            name="Lviv",
            closest_big_city="Kyiv",
        )
        self.route = Route.objects.create(
            source=self.airport,
            destination=self.destination,
            distance=600
        )

    def test_list_routes_authenticated(self):
        result = self.client.get(ROUTE_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_retrieve_detail_route_authenticated(self):
        url = route_detail_url(self.route)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_route_authenticated_forbidden(self):
        payload = {
            "source":self.airport.id,
            "destination":self.destination.id,
            "distance":600
        }
        result_request = self.client.post(ROUTE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="PASSWORD",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.airport = Airport.objects.create(
            name="Kyiv",
            closest_big_city="Lviv",
        )
        self.destination = Airport.objects.create(
            name="Lviv",
            closest_big_city="Kyiv",
        )
        self.route = Route.objects.create(
            source=self.airport,
            destination=self.destination,
            distance=600
        )
    def test_create_route_admin(self):
        payload = {
            "source":self.airport.id,
            "destination":self.destination.id,
            "distance":600
        }
        result_request = self.client.post(ROUTE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Route.objects.filter(
            source=self.airport,
            destination=self.destination,
            distance=600
        ).exists())

    def test_update_route_admin(self):
        new_source = Airport.objects.create(
            name="London",
            closest_big_city="Paris",
        )
        new_destination = Airport.objects.create(
            name="Paris",
            closest_big_city="London",
        )
        url = route_detail_url(self.route)
        payload = {
            "source": new_source.id,
            "destination": new_destination.id,
            "distance": 800
        }
        result_request = self.client.put(url, payload)
        self.assertEqual(result_request.status_code, status.HTTP_200_OK)
        self.route.refresh_from_db()
        self.assertEqual(self.route.source.id, new_source.id)
        self.assertEqual(self.route.destination.id, new_destination.id)
        self.assertEqual(self.route.distance, 800)


    def test_delete_route_admin(self):
        url = route_detail_url(self.route)
        result_request = self.client.delete(url)
        self.assertEqual(result_request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())
