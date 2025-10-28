from django.utils import timezone
from datetime import datetime, time
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer
from users.views import AdminOnlyMixin
from activitylog.views import ActivityLogMixin
from notifications.models import Notification
from members.models import ProjectMember
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Project"])
class AddProject(AdminOnlyMixin, ActivityLogMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)

        Notification.objects.create(
            user=self.request.user,
            title="مشروع جديد",
            message=f"تم إنشاء المشروع: {project.name}"
        )

    def perform_update(self, serializer):
        project = serializer.save()

        if project.status.lower() == "done":
          for user in project.assigned_to.all():
           Notification.objects.create(
            user=user,
            title="انتهاء المشروع",
            message=f"المشروع '{project.name}' انتهى وتم تحديث حالته."
        )


        now = timezone.now()
        if project.due_date:
          if isinstance(project.due_date, datetime):
            due_datetime = project.due_date
          else:
            due_datetime = datetime.combine(project.due_date, time.min)
            due_datetime = timezone.make_aware(due_datetime, timezone.get_current_timezone())

        diff_days = (due_datetime.date() - now.date()).days
        if diff_days == 3:
          for user in project.assigned_to.all():
            Notification.objects.create(
                user=user,
                title="قرب موعد تسليم المشروع",
                message=f"المشروع '{project.name}' سيسلم خلال 3 أيام."
            )


    # Add Cache
    def list(self, request, *args, **kwargs):
        data = cache.get('all_projects') 
        if not data:
            data = ProjectSerializer(self.get_queryset(), many=True).data
            cache.set('all_projects', data, timeout=60*5)  
            print("📦 Loaded from DB")
        else:
            print("⚡ Loaded from Cache")
        return Response(data)