import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from flight.tests.helpers import create_flight
from order.models import Order, Ticket

ORDER_CANCEL_URL = reverse("order:order-cancel", args=[id])

User = get_user_model()

class OrderCancelApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@gmail.com",
            password="PASSWORD",
        )
        self.client.force_authenticate(user=self.user)

    def test_cancel_order_without_tickets(self):
        order = Order.objects.create(user=self.user)
        url = reverse("order:order-cancel", args=[order.id])
        result = self.client.post(url)
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_cancel_order_more_than_24h_before_departure(self):
        flight = create_flight(
            departure_time=datetime.datetime(
                2027, 1, 1, 10, 0, tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2027, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
            ),
        )
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight, order=order, row=1, seat=1, price=100)
        url = reverse("order:order-cancel", args=[order.id])
        result = self.client.post(url)
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_cancel_order_less_than_24h_before_departure(self):
        soon = timezone.now() + datetime.timedelta(hours=2)
        flight = create_flight(
            departure_time=soon,
            arrival_time=soon + datetime.timedelta(hours=2),
        )
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight, order=order, row=1, seat=1, price=100)
        url = reverse("order:order-cancel", args=[order.id])
        result = self.client.post(url)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Order.objects.filter(id=order.id).exists())
