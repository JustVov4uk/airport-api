from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

STATISTIC_URL = reverse("statistics")

User = get_user_model()

class StatisticsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@gmail.com",
            password="PASSWORD",
            is_staff=True,
        )

    def test_statistics_admin(self):
        self.client.force_authenticate(user=self.admin)
        result = self.client.get(STATISTIC_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn("total_flights", result.data)
        self.assertIn("total_orders", result.data)
        self.assertIn("total_tickets", result.data)
        self.assertIn("total_passengers", result.data)

    def test_statistics_forbidden_for_user(self):
        self.user = User.objects.create_user(
            email="user@email.com",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)
        result = self.client.get(STATISTIC_URL)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistics_anonymous(self):
        result = self.client.get(STATISTIC_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
