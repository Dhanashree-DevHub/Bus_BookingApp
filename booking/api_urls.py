from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .import api_views
from .api_views import (BusListView)

urlpatterns = [
    path('auth/register/', api_views.register, name='api_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('buses/', BusListView.as_view(), name='api_bus_list'),
    path('buses/<int:pk>/', api_views.Bus_details, name='api_bus_detail'),
    path('buses/search/', api_views.search_buses, name='api_bus_search')
]