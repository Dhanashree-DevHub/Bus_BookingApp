import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bus_booking.settings')

app = Celery('bus_booking')
app.config_from_object('django.config:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request!r}')
    