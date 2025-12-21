from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Bus(models.Model):
    bus_name = models.CharField(max_length=200)
    bus_number = models.CharField(max_length=20, unique=True)
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    journey_duration = models.CharField(max_length=50, help_text="e.g., 8 hours 30 minutes")
    
    def __str__(self):
        return f"{self.bus_name} ({self.bus_number})"
    
    class Meta:
        verbose_name_plural = "Buses"
        
class Booking(models.Model):
    PAYMENT_STATUS =[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    booking_date = models.DateField()
    seats_booked = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_time = models.DateTimeField(auto_now_add=True)
    passenger_name = models.CharField(max_length=20)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    order_id = models.CharField(max_length=200, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    booking_reference = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.user.username}"
    
    def get_available_seats(bus, date):
        booked = Booking.objects.filter(
            bus=bus, 
            booking_date=date,
            payment_status='completed'
        ).aggregate(total=models.Sum('seats_booked'))['total'] or 0
        return bus.total_seats - booked
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random
            import string
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)