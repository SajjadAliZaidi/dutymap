from .constants import LOCATION_FIELDS
from .hos import calculate_hos
from .log_sheets import split_by_calendar_day
from .routing import fetch_route, geocode
from .svg_log import render_log_sheet


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


def _generate_log_sheets(trip, legs):
    """Compute HOS segments, split by calendar day, render SVGs, save to trip.logs."""
    if trip.start_datetime is None or len(legs) != 2:
        return

    leg1, leg2 = legs
    segments = calculate_hos(
        leg1["duration_hours"], leg1["distance_miles"],
        leg2["duration_hours"], leg2["distance_miles"],
        trip.current_cycle_used,
    )
    if not segments:
        return

    day_groups = split_by_calendar_day(segments, trip.start_datetime)

    trip.logs = [
        {"date": day.isoformat(), "svg": render_log_sheet(day, segs)}
        for day, segs in day_groups.items()
    ]


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

    _generate_log_sheets(trip, route["legs"])

    trip.save()

    return trip
