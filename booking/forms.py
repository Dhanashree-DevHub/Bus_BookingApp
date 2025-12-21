from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2')
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats_booked','passenger_name', 'passenger_phone']
        widgets = {
            'seats_booked': forms.NumberInput(attrs={'min':1, 'class':'form-input'}),
            'passenger_name':forms.TextInput(attrs={'class':'form-input'}),
            'passenger_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'passenger_phone': forms.TextInput(attrs={'class':'form-input','placeholder': '+91-XXXXXXXXXX'}),
        }