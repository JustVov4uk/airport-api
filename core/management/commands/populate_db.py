import datetime

from django.core.management import BaseCommand
from django.utils import timezone

from airplane.models import AirplaneType, Airplane
from airport.models import Country, City, Airport, Route
from flight.models import Crew, Flight

COUNTRIES = ["Ukraine", "England", "France", "Germany", "Spain"]

CITIES = [
    ("Kyiv", "Ukraine"),
    ("Lviv", "Ukraine"),
    ("London", "England"),
    ("Paris", "France"),
    ("Berlin", "Germany"),
    ("Barcelona", "Spain"),
]

AIRPORTS = [
    ("Boryspil International Airport", "Kyiv"),
    ("Lviv Danylo Halytskyi Airport", "Lviv"),
    ("London Heathrow Airport", "London"),
    ("Charles de Gaulle Airport", "Paris"),
    ("Berlin Brandenburg Airport", "Berlin"),
    ("Barcelona El Prat Airport", "Barcelona"),
]

AIRPLANE_TYPES = ["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380"]

AIRPLANES = [
    ("UA-001", 30, 6, "Boeing 737"),
    ("UA-002", 25, 6, "Airbus A320"),
    ("UK-001", 40, 9, "Boeing 777"),
    ("FR-001", 50, 10, "Airbus A380"),
]

CREWS = [
    ("John", "Smith"),
    ("Maria", "Johnson"),
    ("Oleksiy", "Kovalenko"),
    ("Anna", "Petrenko"),
    ("James", "Brown"),
    ("Sophia", "Williams"),
]

ROUTES = [
    ("Boryspil International Airport", "London Heathrow Airport", 2500),
    ("Boryspil International Airport", "Charles de Gaulle Airport", 2100),
    ("London Heathrow Airport", "Berlin Brandenburg Airport", 930),
    ("Charles de Gaulle Airport", "Barcelona El Prat Airport", 1000),
    ("Lviv Danylo Halytskyi Airport", "Berlin Brandenburg Airport", 1400),
]

class Command(BaseCommand):
    help = "Populate database with test data"

    def handle(self, *args, **options):
        self.stdout.write("Populating database...")
        self._create_countries()
        self._create_cities()
        self._create_airports()
        self._create_airplane_types()
        self._create_airplanes()
        self._create_crews()
        self._create_routes()
        self._create_flights()
        self.stdout.write(self.style.SUCCESS("Done!"))

    def _create_countries(self):
        for name in COUNTRIES:
            country, created = Country.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"Created country: {name}")

    def _create_cities(self):
        for city_name, country_name in CITIES:
            country = Country.objects.get(name=country_name)
            city, created = City.objects.get_or_create(
                name=city_name,
                country=country,
            )
            if created:
                self.stdout.write(f"Created city: {city_name}")

    def _create_airports(self):
        for airport_name, city_name in AIRPORTS:
            city = City.objects.get(name=city_name)
            airport, created = Airport.objects.get_or_create(
                name=airport_name,
                city=city,
            )
            if created:
                self.stdout.write(f"Created airport: {airport_name}")

    def _create_airplane_types(self):
        for name in AIRPLANE_TYPES:
            airplane_type, created = AirplaneType.objects.get_or_create(
                name=name,
            )
            if created:
                self.stdout.write(f"Created airplane type: {name}")

    def _create_airplanes(self):
        for name, rows, seats_in_row, type_name in AIRPLANES:
            airplane_type = AirplaneType.objects.get(name=type_name)
            airplane, created = Airplane.objects.get_or_create(
                name=name,
                defaults={
                    "rows": rows,
                    "seats_in_row": seats_in_row,
                    "airplane_type": airplane_type,
                }
            )
            if created:
                self.stdout.write(f"Created airplane: {name}")

    def _create_crews(self):
        for first_name, last_name in CREWS:
            crew, created = Crew.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
            )
            if created:
                self.stdout.write(f"Created crew: {first_name} {last_name}")

    def _create_routes(self):
        for source_name, destination_name, distance in ROUTES:
            source = Airport.objects.get(name=source_name)
            destination = Airport.objects.get(name=destination_name)
            route, created = Route.objects.get_or_create(
                source=source,
                destination=destination,
                defaults={
                    "distance": distance,
                }
            )
            if created:
                self.stdout.write(f"Created route: {source.name} -> {destination.name}")

    def _create_flights(self):
        routes = list(Route.objects.all())
        airplanes = list(Airplane.objects.all())
        crews = list(Crew.objects.all())

        now = timezone.now()
        flights_data = [
            (routes[0], airplanes[0], now + datetime.timedelta(days=1), now + datetime.timedelta(days=1, hours=3),
             "150.00"),
            (routes[1], airplanes[1], now + datetime.timedelta(days=2), now + datetime.timedelta(days=2, hours=3),
             "120.00"),
            (routes[2], airplanes[2], now + datetime.timedelta(days=3), now + datetime.timedelta(days=3, hours=2),
             "200.00"),
            (routes[3], airplanes[3], now + datetime.timedelta(days=4), now + datetime.timedelta(days=4, hours=2),
             "180.00"),
            (routes[4], airplanes[0], now + datetime.timedelta(days=5), now + datetime.timedelta(days=5, hours=2),
             "100.00"),
        ]

        for route, airplane, departure, arrival, price in flights_data:
            flight, created = Flight.objects.get_or_create(
                route=route,
                airplane=airplane,
                departure_time=departure,
                defaults={
                    "arrival_time": arrival,
                    "base_price": price,
                }
            )
            if created:
                flight.crew.set(crews[:2])
                self.stdout.write(f"Created flight: {route}")
