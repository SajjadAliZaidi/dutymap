from rest_framework import serializers
from .branding import BUILT_BY
from .constants import LOCATION_FIELDS
from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    route = serializers.SerializerMethodField()
    logs = serializers.ListField(default=list, read_only=True)
    meta = serializers.SerializerMethodField()

    current_lat = serializers.FloatField(
        required=False, write_only=True, min_value=-90, max_value=90
    )
    current_lon = serializers.FloatField(
        required=False, write_only=True, min_value=-180, max_value=180
    )
    pickup_lat = serializers.FloatField(
        required=False, write_only=True, min_value=-90, max_value=90
    )
    pickup_lon = serializers.FloatField(
        required=False, write_only=True, min_value=-180, max_value=180
    )
    dropoff_lat = serializers.FloatField(
        required=False, write_only=True, min_value=-90, max_value=90
    )
    dropoff_lon = serializers.FloatField(
        required=False, write_only=True, min_value=-180, max_value=180
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_cycle_used",
            "created_at",
            "current_lat",
            "current_lon",
            "pickup_lat",
            "pickup_lon",
            "dropoff_lat",
            "dropoff_lon",
            "route",
            "logs",
            "meta",
        ]
        read_only_fields = ["id", "created_at", "route", "logs", "meta"]

    def validate(self, attrs):
        errors = {}
        for field in LOCATION_FIELDS:
            has_place = bool((attrs.get(field.location) or "").strip())
            has_lat = field.lat in attrs
            has_lon = field.lon in attrs

            if has_lat != has_lon:
                errors[field.lat if not has_lat else field.lon] = (
                    f"Provide both latitude and longitude for the {field.label.lower()} location."
                )
            elif not has_place and not (has_lat and has_lon):
                errors[field.location] = (
                    f"Provide a place name or coordinates for the {field.label.lower()} location."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        for field in LOCATION_FIELDS:
            validated_data.pop(field.lat, None)
            validated_data.pop(field.lon, None)
        return super().create(validated_data)

    def get_meta(self, obj):
        return {"built_by": BUILT_BY}

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
