from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .exceptions import GeocodingError, RoutingError
from .models import Trip
from .routing import search_locations
from .serializers import TripSerializer
from .services import process_trip


@api_view(["GET"])
def geocode_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"suggestions": []}, status=status.HTTP_200_OK)

    try:
        suggestions = search_locations(query, limit=5)
    except GeocodingError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_trip(request):
    serializer = TripSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    trip = serializer.save()

    try:
        process_trip(trip, serializer.validated_data)
    except (GeocodingError, RoutingError) as e:
        trip.route_error = str(e)
        trip.save()
        code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, GeocodingError)
            else status.HTTP_502_BAD_GATEWAY
        )
        return Response({"error": str(e)}, status=code)

    return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def retrieve_trip(request, pk):
    try:
        trip = Trip.objects.get(pk=pk)
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(TripSerializer(trip).data)
