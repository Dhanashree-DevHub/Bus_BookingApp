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
        
#Testcases: Views

class LoginViewTest(BaseTestcase):
    def test_login_success(self):
        response = self.client.post(reverse('login'),{
            'username':'testuser',
            'pasword':'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        
class SignupViewTest(BaseTestcase):
    def setUp(self):
        self.client=Client()
    def tearDown(self):
        User.objects.all().delete()
        
    def test_signup(self):
        response = self.client.post(reverse('signup'),{
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
class HomeViewTest(BaseTestcase):
    def test_home(self):
        self.client.login(username='testuser',password='testpass123')
        response=self.client.get(reverse('home'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'Test Express')
        
class SearchBusesViewTest(BaseTestcase):
    def test_search_buses(self):
        self.client.login(username='testuser',password='testpass123')
        response = self.client.get(reverse('search_buses'),{
            'source': 'Delhi',
            'date':'2025-01-15'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Express')
        
class BookBusViewTest(BaseTestcase):
    def test_create_booking(self):
        self.client.login(username='testuser', password='testpass123')
        Booking.objects.all().delete()
        response = self.client.post(reverse('book_bus', kwargs={'bus_id': self.bus.id}) + '?date=2025-01-15',{
            'seats_booked': 2,
                'passenger_name': 'New User',
                'passenger_email': 'new@example.com',
                'passenger_phone': '+91-9876543210'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(passenger_name='New User').exists())

class ModifyBookingViewTest(BaseTestcase):
    def test_modify_booking(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('modify_booking', kwargs={'booking_id': self.booking.id}),
            {
                'seats_booked': 3,
                'passenger_name': 'Updated Name',
                'passenger_email': 'test@example.com',
                'passenger_phone': '+91-9876543210'
            }
        )
        
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.seats_booked, 3)
        self.assertEqual(self.booking.passenger_name, 'Updated Name')

#Testcases for API views
class APITest(TestCase):
    def setUp(self):
        self.api_client = APIClient()
    def tearDown(self):
        User.objects.all().delete()
        
    def test_register_user(self):
        response = self.api_client.post(reverse('api_register'),{
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertTrue(User.objects.filter(username='apiuser').exists())
        
class APIBusListTest(BaseTestcase):
    def test_get_bus(self):
        response = self.api_client.post(reverse('api_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })

        access_token = response.data['access']

        # Set JWT header
        self.api_client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token
        )
        response = self.api_client.get(reverse('api_bus_list'))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['bus_name'],'Test Express')

class APIBusDetailTest(BaseTestcase):
    def test_bus_details(self):
        response = self.api_client.get(reverse('api_bus_detail'),
                                       
                                       kwargs={'bus_id': self.bus.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
class APICreateBookingTest(BaseTestcase):
    def test_create_booking(self):
        self.api_client.force_authenticate(user=self.user)
        Booking.objects.all().delete()
        response = self.api_client.post(reverse('api_create_booking'), {
            'bus': self.bus.id,
            'booking_date': '2025-01-15',
            'seats_booked': 2,
            'passenger_name': 'API User',
            'passenger_email': 'api@example.com',
            'passenger_phone': '+91-9876543210'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
class APIMyBookingsTest(BaseTestcase):
    def test_get_my_bookings(self):
        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.get(reverse('api_my_bookings'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
class APIModifyBookingTest(BaseTestcase):
    def test_modify_booking(self):
        self.api_client.force_authenticate(user=self.user)
        
        response = self.api_client.put(
            f'/api/bookings/{self.booking.id}/modify/',
            {'seats_booked': 3},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.seats_booked, 3)
        
class APICancelBookingTest(BaseTestcase):
    def test_cancel_booking(self):
        self.api_client.force_authenticate(user=self.user)
        
        response = self.api_client.post(f'/api/bookings/{self.booking.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'cancelled')
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
        