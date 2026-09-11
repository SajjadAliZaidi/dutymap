class GeocodingError(Exception):
    """Raised when geocoding a location fails."""


class RoutingError(Exception):
    """Raised when OSRM route calculation fails."""
