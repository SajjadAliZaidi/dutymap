from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Trip
from .serializers import TripSerializer


@api_view(["POST"])
def create_trip(request):
    serializer = TripSerializer(data=request.data)
    if serializer.is_valid():
        trip = serializer.save()
        return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
