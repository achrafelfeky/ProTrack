from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # 🧩 تحديد إعدادات Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'managementproject.settings')

# # 🧠 إنشاء كائن Celery
# app = Celery('managementproject')

# # ⚙️ تحميل إعدادات Celery من إعدادات Django
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # 🔍 البحث التلقائي عن المهام داخل جميع التطبيقات (tasks.py)
# app.autodiscover_tasks()


# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'managementproject.settings')

app = Celery('managementproject')

# تحميل إعدادات Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# البحث عن المهام داخل كل التطبيقات
app.autodiscover_tasks()

# مهام مجدولة (Celery Beat)
app.conf.beat_schedule = {
    'check-expired-projects-every-minute': {
        'task': 'projects.tasks.check_expired_projects',
        'schedule': crontab(minute='*/1'),  
    },
    'check-upcoming-tasks-every-15-mins': {
        'task': 'projects.tasks.check_upcoming_tasks',
        'schedule': crontab(minute='*/15'),
    },
    'check-expired-tasks-every-30-mins': {
        'task': 'projects.tasks.check_expired_tasks',
        'schedule': crontab(minute='*/30'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
