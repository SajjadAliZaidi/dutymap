from rest_framework import serializers
from .branding import BUILT_BY
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

    LOCATION_FIELDS = (
        ("current_location", "current_lat", "current_lon", "Current"),
        ("pickup_location", "pickup_lat", "pickup_lon", "Pickup"),
        ("dropoff_location", "dropoff_lat", "dropoff_lon", "Dropoff"),
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
        for loc_field, lat_field, lon_field, label in self.LOCATION_FIELDS:
            has_place = bool((attrs.get(loc_field) or "").strip())
            has_lat = lat_field in attrs
            has_lon = lon_field in attrs

            if has_lat != has_lon:
                missing = lat_field if not has_lat else lon_field
                errors[missing] = (
                    f"Provide both latitude and longitude for the {label.lower()} location."
                )
            elif not has_place and not (has_lat and has_lon):
                errors[loc_field] = (
                    f"Provide a place name or coordinates for the {label.lower()} location."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        for _, lat_field, lon_field, _ in self.LOCATION_FIELDS:
            validated_data.pop(lat_field, None)
            validated_data.pop(lon_field, None)
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
