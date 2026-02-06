from django.contrib import admin

from airport.models import Airport, Route


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
