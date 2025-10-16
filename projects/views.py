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


class AddProject(AdminOnlyMixin, ActivityLogMixin, viewsets.ModelViewSet):
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
            members = ProjectMember.objects.filter(project=project)
            for member in members:
                Notification.objects.create(
                    user=member.user,
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

            diff_days = (due_datetime - now).days

            if diff_days == 3:
                members = ProjectMember.objects.filter(project=project)
                for member in members:
                    Notification.objects.create(
                        user=member.user,
                        title="قرب موعد تسليم المشروع",
                        message=f"المشروع '{project.name}' سيسلم خلال 3 أيام."
                    )
