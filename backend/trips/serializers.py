from rest_framework import serializers
from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    route = serializers.DictField(default=dict, read_only=True)
    logs = serializers.ListField(default=list, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_cycle_used",
            "created_at",
            "route",
            "logs",
        ]
        read_only_fields = ["id", "created_at", "route", "logs"]
