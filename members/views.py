from .serializers import ProjectMemberSerializer
from rest_framework import status
from .models import ProjectMember
from rest_framework import viewsets
from users.views import AdminOnlyMixin
from notifications.models import Notification
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from drf_spectacular.utils import extend_schema




@extend_schema(tags=["Project Member"])
class ProjectMemberViewSet( AdminOnlyMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
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
    # Add Cache
    def list(self, request, *args, **kwargs):
        data = cache.get('all_members') 
        if not data:
            data = ProjectMemberSerializer(self.get_queryset(), many=True).data
            cache.set('all_members', data, timeout=60*5)  
            print("📦 Loaded from DB")
        else:
            print("⚡ Loaded from Cache")
        return Response(data)


