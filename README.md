# 🚌 Bus Booking System

A comprehensive Django-based bus booking application with payment gateway integration, real-time seat availability, and automated email notifications.

## Features

- ✅ User Authentication (Login, Signup, Logout)
- 🔍 Advanced Bus Search (by date, source, destination)
- 💺 Real-time Seat Availability
- 💳 Payment Gateway Integration (Razorpay)
- 📧 Automated Email Notifications (Celery + Redis)
- 🕐 Journey Duration & Timing
- 📱 Responsive Design
- 🐳 Docker Support

## Tech Stack

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **Payment**: Razorpay
- **Email**: SMTP (Gmail)
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker & Docker Compose
- Git

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bus-booking.git
   cd bus-booking
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations (in new terminal)**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## Manual Setup (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL and Redis**
   ```bash
   # Install PostgreSQL and Redis
   sudo apt-get install postgresql redis-server
   
   # Create database
   sudo -u postgres psql
   CREATE DATABASE bus_booking_db;
   \q
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start services**
   ```bash
   # Terminal 1: Django
   python manage.py runserver
   
   # Terminal 2: Celery
   celery -A bus_booking worker --loglevel=info
   
   # Terminal 3: Redis
   redis-server
   ```
## Configuration

### Email Setup (Gmail)
1. Enable 2-Step Verification in Google Account
2. Generate App Password: Account Settings → Security → App Passwords
3. Update `.env` with your email and app password

### Razorpay Setup
1. Sign up at https://razorpay.com
2. Get API keys from Dashboard → Settings → API Keys
3. Update `.env` with your Razorpay keys

## Docker Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# View Celery logs
docker-compose logs -f celery