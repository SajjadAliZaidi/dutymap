from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .exceptions import GeocodingError, RoutingError
from .serializers import TripSerializer
from .services import process_trip


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
