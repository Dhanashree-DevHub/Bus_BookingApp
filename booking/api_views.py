from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from rest_framework.generics import ListAPIView, RetrieveAPIView
from datetime import datetime
from .models import Bus, Booking
from .serializers import (
    UserSerializer, BusSerializer, BookingSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Registration successful','access': str(refresh.access_token),'refresh':str(refresh)
        }, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusListView(ListAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated]
    
@api_view(['GET'])
@permission_classes([AllowAny])
def Bus_details(request, pk):
    try:
        bus = Bus.objects.get(pk=pk)
        serializer = BusSerializer(bus)
        return Response(serializer.data)
    except Bus.DoesNotExist:
        return Response({'error':'Bus not found'}, status=status.HTTP_404_NOT_FOUND)
    
# class BusDetailView(RetrieveAPIView):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer
#     permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([AllowAny])
def search_buses(request):
    source = request.GET.get('source','')
    destination = request.GET.get('destination','')
    buses = Bus.objects.all()
    
    if source:
        buses = buses.filter(source__icontains=source)
    if destination:
        buses = buses.filter(destination__icontains=destination)
    serializer = BusSerializer(buses, many=True)
    
    return Response({'count': buses.count(),'results':serializer.data})