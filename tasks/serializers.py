from rest_framework import serializers
from .models import Task
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Task
        fields = '__all__'



