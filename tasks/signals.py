from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Task

# اضافه او تعديل او حذف task الكاش بيتحذف تلقائي
@receiver([post_save, post_delete], sender=Task)
def clear_tasks_cache(sender, **kwargs):
    cache.delete('all_tasks')
    print("Cache cleared due to changes in Tasks")
