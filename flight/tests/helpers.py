import datetime

from airplane.models import Airplane, AirplaneType
from airport.models import Airport, City, Country, Route
from flight.models import Crew, Flight


def create_country(**kwargs):
    defaults = {
        "name": "Ukraine",
    }
    defaults.update(kwargs)
    return Country.objects.create(**defaults)


def create_city(**kwargs):
    defaults = {
        "name": "Kyiv",
        "country": create_country(),
    }
    defaults.update(kwargs)
    return City.objects.create(**defaults)


def create_airport(**kwargs):
    defaults = {"name": "Boryspil", "city": create_city()}
    defaults.update(kwargs)
    return Airport.objects.create(**defaults)


def create_route(**kwargs):
    defaults = {
        "source": create_airport(),
        "destination": create_airport(name="Lviv"),
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
    crew = kwargs.pop("crew", None)
    defaults = {
        "route": create_route(),
        "airplane": create_airplane(),
        "departure_time": datetime.datetime(
            2026, 6, 1, 10, 0, tzinfo=datetime.timezone.utc
        ),
        "arrival_time": datetime.datetime(
            2026, 6, 1, 12, 0, tzinfo=datetime.timezone.utc
        ),
        "base_price": 100,
    }
    defaults.update(kwargs)
    flight = Flight.objects.create(**defaults)
    if crew:
        flight.crew.add(crew)
    return flight
