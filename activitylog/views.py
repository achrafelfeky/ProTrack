from .serializers import ActivityLogSerializer
from rest_framework import status
from .models import ActivityLog
from rest_framework import viewsets


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer




class ActivityLogger:
    @staticmethod
    def log(user, action, instance=None):
        ActivityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            project=getattr(instance, 'project', None),
            action=action,
        )




class ActivityLogMixin:
    """
    Mixin يقوم بتسجيل كل العمليات (إنشاء - تعديل - حذف)
    لأي ModelViewSet يرث منه.
    """
    def perform_create(self, serializer):
        instance = serializer.save()
        ActivityLogger.log(
            user=self.request.user,
            action=f"Created {instance.__class__.__name__}: {instance}",
            instance=instance
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        ActivityLogger.log(
            user=self.request.user,
            action=f"Updated {instance.__class__.__name__}: {instance}",
            instance=instance
        )

    def perform_destroy(self, instance):
        ActivityLogger.log(
            user=self.request.user,
            action=f"Deleted {instance.__class__.__name__}: {instance}",
            instance=instance
        )
        instance.delete()
