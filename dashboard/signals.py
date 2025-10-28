from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from users.models import User
from projects.models import Project
from members.models import ProjectMember
from tasks.models import Task
print("⚡ signals file loaded")


#   مسح الكاش الخاص بيوزر معين
def clear_user_cache(user_id):
    cache.delete(f"user_{user_id}_dashboard_tasks")
    cache.delete(f"user_{user_id}_projects_dashboard")
    print(f"🧹 Cleared cache for user {user_id}")


# المفتاح الأساسي المستخدم في الـ Dashboard View
DASHBOARD_CACHE_KEY = "dashboard_admin_manager"


#  عند تعديل أو حذف يوزر
@receiver([post_save, post_delete], sender=User)
def user_cache_handler(sender, instance, **kwargs):
    clear_user_cache(instance.id)
    cache.delete(DASHBOARD_CACHE_KEY) 
    print(f"🧹 Dashboard cache cleared due to user change: {instance.username}")


#  عند تعديل أو حذف مشروع
@receiver([post_save, post_delete], sender=Project)
def project_cache_handler(sender, instance, **kwargs):
    cache.delete(DASHBOARD_CACHE_KEY)
    print(f"🧹 Dashboard cache cleared due to change in project {instance.name}")


# عند تعديل أو حذف عضو مشروع
@receiver([post_save, post_delete], sender=ProjectMember)
def member_cache_handler(sender, instance, **kwargs):
    clear_user_cache(instance.user.id)
    cache.delete(DASHBOARD_CACHE_KEY)
    print(f"🧹 Dashboard cache cleared due to member {instance.user.username}")


@receiver([post_save, post_delete], sender=Task)
def task_cache_handler(sender, instance, **kwargs):
    for user in instance.assigned_to.all():
        clear_user_cache(user.id)

    cache.delete(DASHBOARD_CACHE_KEY)
    print(f"🧹 Dashboard cache cleared due to task change: {instance.title}")


from django.db.models.signals import m2m_changed

@receiver(m2m_changed, sender=Task.assigned_to.through)
def task_assigned_users_changed(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        for user in instance.assigned_to.all():
            clear_user_cache(user.id)
        cache.delete(DASHBOARD_CACHE_KEY)
        print(f"🧹 Dashboard cache cleared due to assigned users change in task: {instance.title}")
