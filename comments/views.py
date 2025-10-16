from .serializers import CommentSerializer
from rest_framework import status
from .models import Comment
from rest_framework import viewsets
from activitylog.views import ActivityLogMixin
from users.views import CommentPermissionMixin
#, ActivityLogMixin
class Comment(CommentPermissionMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
