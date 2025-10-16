from .serializers import ProjectMemberSerializer
from rest_framework import status
from .models import ProjectMember
from rest_framework import viewsets
from users.views import AdminOnlyMixin
from notifications.models import Notification
from projects.models import Project
from users.models import User


class ProjectMemberViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        user = User.objects.get(id=user_id)

        project_member = serializer.save(user=user)

        Notification.objects.create(
            user=user,
            title="تمت إضافتك إلى المشروع",
            message=f"تمت إضافتك كـ {project_member.role} في المشروع '{project_member.project.name}'"
        )


