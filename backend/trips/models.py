from django.db import models


class Trip(models.Model):
    current_location = models.CharField(max_length=255, blank=True)
    pickup_location = models.CharField(max_length=255, blank=True)
    dropoff_location = models.CharField(max_length=255, blank=True)
    current_cycle_used = models.FloatField(help_text="Hours used in current cycle")
    start_datetime = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Route data (populated after geocoding + OSRM)
    route_geometry = models.JSONField(null=True, blank=True)
    distance_miles = models.FloatField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)
    current_coords = models.JSONField(null=True, blank=True)
    pickup_coords = models.JSONField(null=True, blank=True)
    dropoff_coords = models.JSONField(null=True, blank=True)
    route_error = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        pickup = self.pickup_location or self.pickup_coords or "unknown pickup"
        dropoff = self.dropoff_location or self.dropoff_coords or "unknown dropoff"
        return f"Trip from {pickup} to {dropoff} ({self.created_at})"
