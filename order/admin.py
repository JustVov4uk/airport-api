from django.contrib import admin

from flight.models import Flight
from order.models import Order, Ticket


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("row", "seat", "flight", "order")
