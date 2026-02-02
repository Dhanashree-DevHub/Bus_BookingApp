from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Bus, Booking

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'
        
class BookingSerializer(serializers.ModelSerializer):
    bus_name = serializers.CharField(source ='bus.bus_name', read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'booking_reference', 'bus', 'bus_name', 
            'booking_date', 'seats_booked', 'passenger_name',
            'passenger_email', 'passenger_phone', 'total_price',
            'payment_status']
        read_only_fields = ['booking_reference','total_price','payment_status']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
