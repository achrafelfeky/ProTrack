from django.utils import timezone
from datetime import timedelta
from projects.models import Project
from tasks.models import Task
from members.models import ProjectMember
from notifications.models import Notification
from celery import shared_task

# 🔹 1. التحقق من المشاريع المنتهية + إشعار قبل 3 أيام
@shared_task
def check_expired_projects():
    now = timezone.now()

    expired = Project.objects.filter(
        due_date__lte=now
    ).exclude(status="Done")

    # المشاريع القريبة من الانتهاء (قبل 3 أيام)
    soon = now + timedelta(days=3)
    upcoming = Project.objects.filter(
        due_date__lte=soon,
        due_date__gt=now
    )

    for project in expired:
        project.status = "Done"
        project.save()

        members = ProjectMember.objects.filter(project=project)
        for member in members:
            print("Sending notification to:", member.user.username)
            Notification.objects.create(
                user=member.user,
                title="انتهاء المشروع",
                message=f"المشروع '{project.name}' انتهى وتم تحديث حالته."
            )
        

    for project in upcoming:
        members = ProjectMember.objects.filter(project=project)
        for member in members:
            Notification.objects.create(
                user=member.user,
                title="قرب موعد تسليم المشروع",
                message=f"المشروع '{project.name}' سيسلم خلال 3 أيام."
            )


# 🔹 2. التحقق من المهام القريبة من موعد التسليم (قبل ساعة)
@shared_task
def check_upcoming_tasks():
    upcoming_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress']
    )

    for task in upcoming_tasks:
        now = task.current_time_for_check if task.current_time_for_check else timezone.now()
        soon = now + timedelta(hours=1)

        if now < task.due_date <= soon:
            Notification.objects.create(
                user=task.assigned_to,
                title="قرب موعد المهمة",
                message=f"المهمة '{task.title}' باقي ساعة على تسليمها!"
            )


# 🔹 3. التحقق من المهام المنتهية فعلاً (بعد وقت التسليم)
@shared_task
def check_expired_tasks():
    expired_tasks = Task.objects.exclude(status="done")

    for task in expired_tasks:
        now = task.current_time_for_check if task.current_time_for_check else timezone.now()
        if task.due_date <= now:
            task.status = "done"
            task.save()

            Notification.objects.create(
                user=task.assigned_to,
                title="انتهاء المهمة",
                message=f"المهمة '{task.title}' انتهى وقتها وتم تحديث حالتها إلى منتهية."
            )
