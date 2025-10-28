from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from projects.models import Project
from activitylog.models import ActivityLog
from activitylog.views import ActivityLogMixin


class ActivityLogTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='pass123')
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            name="Project 1",
            description="Test project",
            status="todo",
            owner=self.user
        )

        self.url = reverse('activity-list') 

    def test_requires_authentication(self):
        
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# يتأكد إن ActivityLogMixin بيسجل الإنشاء

    def test_log_creation(self):
        mixin = ActivityLogMixin()
        mixin.request = type("req", (), {"user": self.user})()
        mixin.perform_create = lambda serializer: None  
        ActivityLog.objects.create(user=self.user, project=self.project, action="Created Project")

        logs = ActivityLog.objects.all()
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().action, "Created Project")


# يتأكد إن الـ ViewSet بيرجع اللوجات صح
    def test_get_activity_logs(self):

        ActivityLog.objects.create(user=self.user, project=self.project, action="Created something")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Created something", str(response.data))
