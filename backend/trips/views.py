from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .exceptions import GeocodingError, RoutingError
from .models import Trip
from .serializers import TripSerializer
from .routing import geocode, fetch_route


@api_view(["POST"])
def create_trip(request):
    serializer = TripSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    trip = serializer.save()

    # Geocode all three locations
    locations = {
        "current": trip.current_location,
        "pickup": trip.pickup_location,
        "dropoff": trip.dropoff_location,
    }
    coords = {}

    for key, loc in locations.items():
        try:
            coords[key] = geocode(loc)
        except GeocodingError as e:
            trip.route_error = str(e)
            trip.save()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Save coordinates
    trip.current_coords = {"lat": coords["current"]["lat"], "lon": coords["current"]["lon"]}
    trip.pickup_coords = {"lat": coords["pickup"]["lat"], "lon": coords["pickup"]["lon"]}
    trip.dropoff_coords = {"lat": coords["dropoff"]["lat"], "lon": coords["dropoff"]["lon"]}
    trip.save()

    # Fetch driving route
    try:
        route = fetch_route([coords["current"], coords["pickup"], coords["dropoff"]])
    except RoutingError as e:
        trip.route_error = str(e)
        trip.save()
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    trip.route_geometry = route["geometry"]
    trip.distance_miles = route["distance_miles"]
    trip.duration_hours = route["duration_hours"]
    trip.save()

    return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)
