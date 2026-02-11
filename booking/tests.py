import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from booking.models import Bus, Booking
from datetime import date, time
from decimal import Decimal
import json

class BaseTestcase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
            )
        self.bus = Bus.objects.create(
            bus_number='TEST-001',
            bus_name='Test Express',
            source='Delhi',
            destination='Mumbai',
            total_seats=40,
            price=Decimal('1200.00'),
            departure_time=time(9, 0),
            arrival_time=time(21, 30),
            journey_duration='12 hours 30 minutes'
        )
        self.booking = Booking.objects.create(
            user=self.user,
            bus=self.bus,
            booking_date=date.today(),
            seats_booked=2,
            total_price=Decimal('2400.00'),
            passenger_name='Test User',
            passenger_email='test@example.com',
            passenger_phone='+91-9876543210'
        )
        self.client = Client()
        self.api_client = APIClient()
    
    def tearDown(self):
        Booking.objects.all().delete()
        Bus.objects.all().delete()
        User.objects.all().delete()
        
# Testcases for models BUS and BOOKING
class BusModelTest(BaseTestcase):
    def test_bus_model(self):
        self.assertEqual(self.bus.bus_name, 'Test Express')
        self.assertEqual(self.bus.total_seats, 40)
        self.assertEqual(self.bus.bus_number, 'TEST-001')
        
class BookingModelTest(BaseTestcase):
    def test_booking_model(self):
        self.assertEqual(self.booking.seats_booked, 2)
        self.assertIsNotNone(self.booking.booking_reference)
        self.assertEqual(self.booking.total_price, Decimal('2400.00'))

# #Testcases for Bus and Booking Models
# class BusModelTest(TestCase):
#     def test_bus_model(self):
#         bus = Bus.objects.create(
#             bus_number='TEST-001',
#             bus_name='Test Express',
#             source='Delhi',
#             destination='Mumbai',
#             total_seats=40,
#             price=Decimal('1200.00'),
#             departure_time=time(9, 0),
#             arrival_time=time(21, 30),
#             journey_duration='12 hours 30 minutes'
#             )
#         self.assertEqual(bus.bus_name , 'Test Express')
#         self.assertEqual(bus.total_seats, 40)

# class BookingModelTest(TestCase):
#     def test_booking_model(self):
#         user = User.objects.create_user(username='test', password='test123')
#         bus = Bus.objects.create(
#             bus_number='TEST-001',
#             bus_name='Test Express',
#             source='Delhi',
#             destination='Mumbai',
#             total_seats=40,
#             price=Decimal('1200.00'),
#             departure_time=time(9, 0),
#             arrival_time=time(21, 30),
#             journey_duration='12 hours'
#         )
#         booking = Booking.objects.create(
#             user=user,
#             bus=bus,
#             booking_date=date.today(),
#             seats_booked=2,
#             total_price=Decimal('2400.00'),
#             passenger_name='Test User',
#             passenger_email='test@test.com',
#             passenger_phone='+91-1234567890'
#         )
#         self.assertEqual(booking.seats_booked,2)
#         self.assertIsNotNone(booking.booking_reference)
        
# # Testcases for views
# class SignupView(TestCase):
#     def test_signup_success(self):
#         client = Client()
#         response = client.post(reverse('signup'),{
#             'username': 'newuser',
#             'email': 'new@test.com',
#             'password1': 'testpass123',
#             'password2': 'testpass123'
#     })
#         self.assertEqual(response.status_code, 302) #redirect
#         self.assertTrue(User.objects.filter(username='newuser').exists())
        
# class Login_view(TestCase):
#     def test_login_success(self):
#         User.objects.create_user(username='test',password='test123')
#         client = Client()
#         response = client.post(reverse('login'), {
#             'username': 'test',
#             'password':'test123'
#         })
#         self.assertEqual(response.status_code, 302)
        
# class HomeViewTest(TestCase):
#     def test_home_view(self):
        