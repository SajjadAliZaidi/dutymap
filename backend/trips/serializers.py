from rest_framework import serializers
from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    route = serializers.SerializerMethodField()
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

    def get_route(self, obj):
        if obj.route_geometry is None and not obj.route_error:
            return None
        return {
            "geometry": obj.route_geometry,
            "distance_miles": obj.distance_miles,
            "duration_hours": obj.duration_hours,
            "coordinates": {
                "current": obj.current_coords,
                "pickup": obj.pickup_coords,
                "dropoff": obj.dropoff_coords,
            },
            "error": obj.route_error or None,
        }
