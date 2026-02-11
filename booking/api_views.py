from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from rest_framework.views import APIView
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    serializer = BookingSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    bus = serializer.validated_data['bus']
    seats = serializer.validated_data['seats_booked']

    total_price = bus.price * seats

    booking = serializer.save(
        user=request.user,
        total_price=total_price
    )

    return Response(
        {
            'message': 'Booking created successfully',
            'booking': BookingSerializer(booking).data
        },
        status=status.HTTP_201_CREATED
    )

class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).exclude(payment_status='cancelled')
        
        serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            'count': bookings.count(),
            'bookings': serializer.data
        })
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_detail(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
        serializer = BookingSerializer(booking)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modify_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error':'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    if booking.payment_status != 'pending':
        return Response({'error': 'only pending bookings can be modified'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = BookingSerializer(booking, data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    seats = serializer.validated_data.get('seats_booked', booking.seats_booked)
    serializer.save(
        total_price=booking.bus.price * seats
    )
    
    return Response({
        'message':'Booking modified successfully',
        'booking' : serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
         
        if booking.payment_status == 'pending':
            booking.payment_status = 'cancelled'
            booking.save()
            return Response({
                'message': 'Booking cancelled successfully',
                'booking_reference': booking.booking_reference
            })
        else:
            return Response({
                'error': 'Only pending bookings can be cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

             