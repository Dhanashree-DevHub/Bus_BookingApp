from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .import api_views
from .api_views import (BusListView, MyBookingsView)

urlpatterns = [
    path('auth/register/', api_views.register, name='api_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('buses/', BusListView.as_view(), name='api_bus_list'),
    path('buses/<int:pk>/', api_views.Bus_details, name='api_bus_detail'),
    path('buses/search/', api_views.search_buses, name='api_bus_search'),
    path('bookings',MyBookingsView.as_view(), name='api_my_bookings'),
    path('booking/create/', api_views.create_booking, name='api_create_booking'),
    path('bookings/<int:pk>',api_views.booking_detail, name='api_booking_detail'),
    path('bookings/<int:pk>/modify/', api_views.modify_booking, name='api_modify_booking'),
    path('bookings/<int:pk>/cancel/', api_views.cancel_booking, name='api_cancel_booking'),
]