from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Comment

# اضافه او تعديل او حذف كومنت الكاش بيتحذف تلقائي
@receiver([post_save, post_delete], sender=Comment)
def clear_books_cache(sender, **kwargs):
    cache.delete('all_comments')
    print("🧹 Cache cleared due to changes in Comment")
