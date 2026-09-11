from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
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
    errors = []

    for key, loc in locations.items():
        result = geocode(loc)
        if result is None:
            errors.append(f"Could not geocode {key} location: {loc}")
        else:
            coords[key] = result

    if len(coords) < 3:
        trip.route_error = "; ".join(errors)
        trip.save()
        return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)

    # Save coordinates
    trip.current_coords = {"lat": coords["current"]["lat"], "lon": coords["current"]["lon"]}
    trip.pickup_coords = {"lat": coords["pickup"]["lat"], "lon": coords["pickup"]["lon"]}
    trip.dropoff_coords = {"lat": coords["dropoff"]["lat"], "lon": coords["dropoff"]["lon"]}

    # Fetch driving route
    route = fetch_route([coords["current"], coords["pickup"], coords["dropoff"]])
    if route is None:
        trip.route_error = "Could not calculate driving route"
        trip.save()
        return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)

    trip.route_geometry = route["geometry"]
    trip.distance_miles = route["distance_miles"]
    trip.duration_hours = route["duration_hours"]
    trip.save()

    return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)
