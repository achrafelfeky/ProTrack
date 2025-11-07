import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'managementproject.settings')

app = Celery('managementproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True

#  DatabaseScheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-tasks-deadlines-every-day-at-8am': {
        'task': 'tasks.tasks.check_tasks_deadlines',  
        'schedule': crontab(hour=8, minute=0),  
    },
}

8

