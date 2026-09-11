import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "DutyMapELD/1.0"}


def geocode(location: str) -> dict | None:
    """Geocode a location string to lat/lon using Nominatim.

    Returns {"lat": float, "lon": float, "display_name": str} or None.
    """
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": location, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        r = results[0]
        return {
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
            "display_name": r.get("display_name", location),
        }
    except Exception:
        return None


def fetch_route(coords: list[dict]) -> dict | None:
    """Get driving route from OSRM.

    coords: list of {"lat": ..., "lon": ...} in order.
    Returns {"geometry": GeoJSON, "distance_miles": float, "duration_hours": float} or None.
    """
    coord_str = ";".join(f"{c['lon']},{c['lat']}" for c in coords)
    url = f"{OSRM_URL}/{coord_str}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        route = data["routes"][0]
        return {
            "geometry": route["geometry"],
            "distance_miles": round(route["distance"] / 1609.344, 1),
            "duration_hours": round(route["duration"] / 3600, 2),
        }
    except Exception:
        return None
