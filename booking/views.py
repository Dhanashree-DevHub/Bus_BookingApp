from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
import razorpay
import json

from .models import Bus, Booking
from .forms import SignUpForm, BookingForm
from .tasks import send_booking_confirmation_email

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'booking/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'booking/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def home_view(request):
    buses = Bus.objects.all()
    return render(request, 'booking/home.html', {'buses': buses})

@login_required
def search_buses(request):
    date_str = request.GET.get('date')
    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    
    buses = Bus.objects.all()
    if source:
        buses = buses.filter(source__icontains=source)
    if destination:
        buses = buses.filter(destination__icontains=destination)
    
    results = []
    if date_str:
        search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        for bus in buses:
            booked = Booking.objects.filter(
                bus=bus, 
                booking_date=search_date,
                payment_status='completed'
            ).aggregate(total=Sum('seats_booked'))['total'] or 0
            available = bus.total_seats - booked
            results.append({
                'bus': bus,
                'available_seats': available,
                'date': search_date
            })
    
    return render(request, 'booking/search.html', {
        'results': results,
        'date': date_str,
        'source': source,
        'destination': destination
    })

@login_required
def book_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        messages.error(request, 'Please select a date')
        return redirect('home')
    
    booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    booked = Booking.objects.filter(
        bus=bus, 
        booking_date=booking_date,
        payment_status='completed'
    ).aggregate(total=Sum('seats_booked'))['total'] or 0
    available_seats = bus.total_seats - booked
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats_booked']
            if seats > available_seats:
                messages.error(request, f'Only {available_seats} seats available')
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.bus = bus
                booking.booking_date = booking_date
                booking.total_price = bus.price * seats
                booking.save()
                
                # Store booking ID in session for payment
                request.session['pending_booking_id'] = booking.id
                
                return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm(initial={'passenger_email': request.user.email})
    
    return render(request, 'booking/book.html', {
        'bus': bus,
        'form': form,
        'date': date_str,
        'available_seats': available_seats
    })

@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.payment_status == 'completed':
        messages.info(request, 'This booking is already paid')
        return redirect('my_bookings')
    
    # Create Razorpay order
    amount = int(booking.total_price * 100)  # Convert to paise
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1
    })
    
    booking.order_id = razorpay_order['id']
    booking.save()
    
    context = {
        'booking': booking,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'amount': amount,
    }
    
    return render(request, 'booking/payment.html', context)

@csrf_exempt
@login_required
def payment_success(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Update booking
            booking = Booking.objects.get(order_id=order_id)
            booking.payment_status = 'completed'
            booking.payment_id = payment_id
            booking.payment_method = 'Razorpay'
            booking.save()
            
            # Send confirmation email asynchronously
            send_booking_confirmation_email.delay(booking.id)
            
            messages.success(request, 'Payment successful! Booking confirmed.')
            return redirect('booking_success', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('payment_failed')
    
    return redirect('home')

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_success.html', {'booking': booking})

@login_required
def payment_failed(request):
    return render(request, 'booking/payment_failed.html')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user,
        payment_status='completed'
    ).order_by('-booking_time')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.payment_status == 'completed':
        messages.warning(request, 'Cannot cancel confirmed booking. Please contact support.')
    else:
        booking.delete()
        messages.success(request, 'Booking cancelled successfully!')
    return redirect('my_bookings')