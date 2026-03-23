from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from flight.tests.helpers import create_flight
from order.models import Order

ORDER_URL = reverse("order:order-list")

User = get_user_model()

def order_detail_url(order_id):
    return reverse("order:order-detail", args=[order_id])


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_order_anonymous_forbidden(self):
        payload = {}
        result = self.client.post(ORDER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.user2 = User.objects.create_user(
            email="EMAIL2",
            password="PASSWORD",
        )

    def test_create_order_authorized(self):
        self.client.force_authenticate(user=self.user1)
        flight = create_flight()
        payload = {"tickets": [{"flight": flight.id, "row": 1, "seat": 1}]}
        result = self.client.post(ORDER_URL, payload, format="json")
        print(result.data)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user1).exists())

    def test_list_orders_user_sees_only_own(self):
        Order.objects.create(user=self.user1)
        Order.objects.create(user=self.user2)

        self.client.force_authenticate(user=self.user1)
        result = self.client.get(ORDER_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data["results"]), 1)

    def test_retrieve_order_other_user_forbidden(self):
        order_user2 = Order.objects.create(user=self.user2)

        self.client.force_authenticate(user=self.user1)
        url = order_detail_url(order_user2.id)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)


class AdminOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="EMAIL",
            password="PASSWORD",
        )
        self.user2 = User.objects.create_user(
            email="EMAIL2",
            password="PASSWORD",
        )
        self.admin = User.objects.create_user(
            email="admin",
            password="PASSWORD",
            is_staff=True,
        )

    def test_admin_sees_all_orders(self):
        Order.objects.create(user=self.user1)
        Order.objects.create(user=self.user2)

        self.client.force_authenticate(user=self.admin)
        result = self.client.get(ORDER_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data["results"]), 2)
