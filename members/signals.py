from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import ProjectMember

# اضافه او تعديل او حذف عضو الكاش بيتحذف تلقائي
@receiver([post_save, post_delete], sender=ProjectMember)
def clear_members_cache(sender, **kwargs):
    cache.delete('all_members')
    print("🧹 Cache cleared due to changes in ProjectMember")
