from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="EMAIL",
            password="PASSWORD",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(name="Airbus")
        self.airplane = Airplane.objects.create(
            name="A320",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

    def test_create_airplane_admin(self):
        payload = {
            "name": "A320",
            "rows": 25,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        airplane_before = Airplane.objects.count()
        result_request = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(result_request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airplane_before + 1, Airplane.objects.count())

    def test_update_airplane_admin(self):
        url = airplane_detail_url(self.airplane)
        payload = {
            "name": "A380",
            "rows": 25,
            "seats_in_row": 10,
            "airplane_type": self.airplane_type.id,
        }
        result_request = self.client.put(url, payload)
        self.assertEqual(result_request.status_code, status.HTTP_200_OK)
        self.airplane.refresh_from_db()
        self.assertEqual(self.airplane.name, "A380")
        self.assertEqual(self.airplane.seats_in_row, 10)

    def test_delete_airplane_admin(self):
        url = airplane_detail_url(self.airplane)
        result_request = self.client.delete(url)
        self.assertEqual(result_request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airplane.objects.filter(id=self.airplane.id).exists())

    def test_filter_airplanes_by_airplane_type(self):
        self.airplane_type_other = AirplaneType.objects.create(name="Boeing")
        self.airplane_other = Airplane.objects.create(
            name="777",
            rows=50,
            seats_in_row=8,
            airplane_type=self.airplane_type_other,
        )

        result_request = self.client.get(AIRPLANE_URL, {"airplane_type": self.airplane_type_other.id})
        airplane_ids = [item["id"] for item in result_request.data["results"]]
        self.assertNotIn(self.airplane.id, airplane_ids)
        self.assertIn(self.airplane_other.id, airplane_ids)
