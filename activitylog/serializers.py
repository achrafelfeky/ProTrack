from rest_framework import serializers
from .models import ActivityLog
from users.serializers import UserSerializer
from projects.serializers import ProjectSerializer

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ('id', 'user', 'project', 'action', 'created_at')
