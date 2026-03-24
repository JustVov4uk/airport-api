import datetime

from airplane.models import Airplane, AirplaneType
from airport.models import Airport, Route
from flight.models import Crew, Flight
from order.models import Order, Ticket


def create_airport(**kwargs):
    defaults = {"name": "Kyiv", "city": "Lviv"}
    defaults.update(kwargs)
    return Airport.objects.create(**defaults)


def create_route(**kwargs):
    defaults = {
        "source": create_airport(),
        "destination": create_airport(name="Lviv", city="Kyiv"),
        "distance": 600,
    }
    defaults.update(kwargs)
    return Route.objects.create(**defaults)


def create_airplane_type(**kwargs):
    defaults = {"name": "Airbus"}
    defaults.update(kwargs)
    return AirplaneType.objects.create(**defaults)


def create_airplane(**kwargs):
    defaults = {
        "name": "RS-406",
        "rows": 25,
        "seats_in_row": 3,
        "airplane_type": create_airplane_type(),
    }
    defaults.update(kwargs)
    return Airplane.objects.create(**defaults)


def create_crew(**kwargs):
    defaults = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }
    defaults.update(kwargs)
    return Crew.objects.create(**defaults)


def create_flight(**kwargs):
    defaults = {
        "route": create_route(),
        "airplane": create_airplane(),
        "crew": create_crew(),
        "departure_time": datetime.time(10, 00),
        "arrival_time": datetime.time(12, 00),
    }
    defaults.update(kwargs)
    return Flight.objects.create(**defaults)


def create_order(**kwargs):
    defaults = {}
    defaults.update(kwargs)
    return Order.objects.create(**defaults)


def create_ticket(**kwargs):
    defaults = {
        "row": 2,
        "seat": 5,
        "flight": create_flight(),
        "order": create_order(),
    }
    defaults.update(kwargs)
    return Ticket.objects.create(**defaults)
