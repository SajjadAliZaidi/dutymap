from typing import NamedTuple

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "DutyMapELD/1.0"}
TIMEOUT_SECONDS = 10


class LocationField(NamedTuple):
    """Maps a trip stop to its place-name field, coordinate fields, and label."""

    key: str
    location: str
    lat: str
    lon: str
    label: str


LOCATION_FIELDS = (
    LocationField("current", "current_location", "current_lat", "current_lon", "Current"),
    LocationField("pickup", "pickup_location", "pickup_lat", "pickup_lon", "Pickup"),
    LocationField("dropoff", "dropoff_location", "dropoff_lat", "dropoff_lon", "Dropoff"),
)
