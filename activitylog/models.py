from django.db import models
from users.models import User
from django.contrib.auth import get_user_model
User = get_user_model()


class ActivityLog(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"
