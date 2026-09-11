from .constants import LOCATION_FIELDS
from .routing import fetch_route, geocode


def resolve_stop_coordinates(trip, validated_data):
    """Resolve every stop to lat/lon.

    Supplied coordinates win; otherwise the place name is geocoded.
    Returns {key: {"lat": float, "lon": float, "display_name": str}}.
    Raises GeocodingError when a place name cannot be resolved.
    """
    coords = {}
    for field in LOCATION_FIELDS:
        lat = validated_data.get(field.lat)
        lon = validated_data.get(field.lon)
        if lat is not None and lon is not None:
            coords[field.key] = {"lat": lat, "lon": lon, "display_name": f"{lat}, {lon}"}
        else:
            coords[field.key] = geocode(getattr(trip, field.location))
    return coords


def process_trip(trip, validated_data):
    """Resolve the stops and attach the driving route to `trip`.

    Persists coordinates before routing so a routing failure still leaves the
    stops on the trip. Raises GeocodingError or RoutingError.
    """
    coords = resolve_stop_coordinates(trip, validated_data)

    for field in LOCATION_FIELDS:
        resolved = coords[field.key]
        setattr(trip, f"{field.key}_coords", {"lat": resolved["lat"], "lon": resolved["lon"]})
    trip.save()

    route = fetch_route([coords[field.key] for field in LOCATION_FIELDS])

    trip.route_geometry = route["geometry"]
    trip.distance_miles = route["distance_miles"]
    trip.duration_hours = route["duration_hours"]
    trip.save()

    return trip
