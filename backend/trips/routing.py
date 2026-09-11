import requests

from .exceptions import GeocodingError, RoutingError

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "DutyMapELD/1.0"}
TIMEOUT_SECONDS = 10


def geocode(location: str) -> dict:
    """Geocode a location string to lat/lon using Nominatim.

    Returns {"lat": float, "lon": float, "display_name": str}.
    Raises GeocodingError on failure.
    """
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": location, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
    except requests.Timeout:
        raise GeocodingError(f"Geocoding service timed out for: {location}")
    except requests.RequestException as e:
        raise GeocodingError(f"Geocoding service error for {location}: {e}")

    results = resp.json()
    if not results:
        raise GeocodingError(f"Could not find location: {location}")

    r = results[0]
    return {
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "display_name": r.get("display_name", location),
    }


def fetch_route(coords: list[dict]) -> dict:
    """Get driving route from OSRM.

    coords: list of {"lat": ..., "lon": ...} in order.
    Returns {"geometry": GeoJSON, "distance_miles": float, "duration_hours": float}.
    Raises RoutingError on failure.
    """
    coord_str = ";".join(f"{c['lon']},{c['lat']}" for c in coords)
    url = f"{OSRM_URL}/{coord_str}?overview=full&geometries=geojson"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.Timeout:
        raise RoutingError("Routing service timed out")
    except requests.RequestException as e:
        raise RoutingError(f"Routing service error: {e}")

    data = resp.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RoutingError("No driving route found between the specified locations")

    route = data["routes"][0]
    return {
        "geometry": route["geometry"],
        "distance_miles": round(route["distance"] / 1609.344, 1),
        "duration_hours": round(route["duration"] / 3600, 2),
    }
