from django.contrib import admin

from airplane.models import Airplane, AirplaneType


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
