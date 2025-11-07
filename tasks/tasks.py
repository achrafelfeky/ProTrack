from celery import shared_task
from datetime import date, timedelta, datetime
from notifications.models import Notification
from .models import Task

@shared_task
def check_tasks_deadlines():
    today = date.today()
    tomorrow = today + timedelta(days=1)

   # اشعار قبل موعد التسليم بيوم
    upcoming_tasks = Task.objects.filter(due_date=tomorrow, normal_status='no_done')
    for task in upcoming_tasks:
        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                title=" اقتراب موعد التسليم",
                message=f"المهمة '{task.title}' موعد تسليمها غدًا ({task.due_date}). يُرجى إنجازها قبل الموعد!"
            )

   # اشعار عند انتهاء المده
    overdue_tasks = Task.objects.filter(due_date__lte=today, normal_status='no_done')
    for task in overdue_tasks:
        for user in task.assigned_to.all():
            Notification.objects.create(
                user=user,
                title=" انتهى موعد التسليم",
                message=f"المهمة '{task.title}' انتهى موعد تسليمها اليوم ({task.due_date}). تم تحويلها إلى منتهية."
            )
        task.normal_status = 'done'
        task.save()

    print(f"[{datetime.now()}]  تم تنفيذ فحص المواعيد اليومية.")
    return "تم فحص المواعيد اليومية بنجاح"

 # Test
@shared_task
def test_celery_beat():
    print(f"[{datetime.now()}]  Celery Beat يعمل تمام!")
    return "Celery Beat يعمل تمام"
