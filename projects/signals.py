from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Project

# اضافه او تعديل او حذف project الكاش بيتحذف تلقائي
@receiver([post_save, post_delete], sender=Project)
def clear_project_cache(sender, **kwargs):
    cache.delete('all_projects')
    print("🧹 Cache cleared due to changes in Project")
