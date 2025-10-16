from rest_framework import serializers
from .models import ProjectMember
from users.serializers import UserSerializer

class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ('id', 'user', 'project', 'role')
