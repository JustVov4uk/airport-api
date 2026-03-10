from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airplane.models import AirplaneType

AIRPLANE_TYPE_URL = reverse("airplane:airplanetype-list")

def airplane_type_detail_url(airplane_type):
    return reverse("airplane:airplanetype-detail", args={airplane_type.id})


class UnauthenticatedAirplaneTypeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(
            name="Airbus",
        )

    def test_list_airplane_types_anonymous(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_detailed_airplane_type_anonymous(self):
        url = airplane_type_detail_url(self.airplane_type)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_airplane_type_anonymous_forbidden(self):
        payload = {
            "name": "Airbus",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirplaneTypeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(
            name="Airbus",
        )

    def test_create_airplane_type_authorized_forbidden(self):
        payload = {
            "name": "Airbus",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)