from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_booking_confirmation_email(booking_id):
    from .models import Booking
    
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f'Booking Confirmation - {booking.booking_reference}'
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #2563eb; text-align: center;">🚌 Bus Booking Confirmed!</h2>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Booking Details</h3>
                    <p><strong>Booking Reference:</strong> {booking.booking_reference}</p>
                    <p><strong>Passenger Name:</strong> {booking.passenger_name}</p>
                    <p><strong>Bus:</strong> {booking.bus.bus_name} ({booking.bus.bus_number})</p>
                    <p><strong>Route:</strong> {booking.bus.source} → {booking.bus.destination}</p>
                    <p><strong>Journey Date:</strong> {booking.booking_date.strftime('%d %B %Y')}</p>
                    <p><strong>Departure Time:</strong> {booking.bus.departure_time.strftime('%I:%M %p')}</p>
                    <p><strong>Arrival Time:</strong> {booking.bus.arrival_time.strftime('%I:%M %p')}</p>
                    <p><strong>Duration:</strong> {booking.bus.journey_duration}</p>
                    <p><strong>Seats Booked:</strong> {booking.seats_booked}</p>
                </div>
                
                <div style="background: #d1fae5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #065f46;">Payment Details</h3>
                    <p><strong>Total Amount Paid:</strong> ₹{booking.total_price}</p>
                    <p><strong>Payment Status:</strong> {booking.payment_status.upper()}</p>
                    <p><strong>Payment ID:</strong> {booking.payment_id}</p>
                    <p><strong>Payment Method:</strong> {booking.payment_method or 'Online Payment'}</p>
                </div>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">Important Instructions:</h4>
                    <ul>
                        <li>Please carry a valid ID proof while boarding</li>
                        <li>Reach the boarding point 15 minutes before departure</li>
                        <li>Keep this booking reference handy: <strong>{booking.booking_reference}</strong></li>
                    </ul>
                </div>
                
                <p style="text-align: center; color: #666; margin-top: 30px;">
                    Thank you for choosing our service!<br>
                    <small>This is an automated email. Please do not reply.</small>
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.passenger_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Email sent successfully to {booking.passenger_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"