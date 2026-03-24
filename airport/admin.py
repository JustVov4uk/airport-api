from django.contrib import admin

from airport.models import Airport, City, Country, Route


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
