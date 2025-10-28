from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from projects.models import Project
from members.models import ProjectMember
from tasks.models import Task


class DashboardAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()


        self.admin_user = User.objects.create_user(username="admin", email="admin@test.com", password="admin123", role="admin")
        self.manager_user = User.objects.create_user(username="manager", email="manager@test.com", password="manager123", role="manager")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="user123", role="user")
        self.client.force_authenticate(user=self.admin_user)
        self.project = Project.objects.create(
            name="Test Project",
            description="Dashboard test project",
            owner=self.admin_user,
            status="in_progress"
        )

        self.member = ProjectMember.objects.create(
            user=self.manager_user,
            project=self.project,
            role="manager"
        )

        
        self.task1 = Task.objects.create(
            title="Task Done",
            description="Done task",
            status="done",
            project=self.project,
            created_by=self.admin_user
        )

        self.task2 = Task.objects.create(
            title="Task In Progress",
            description="In progress task",
            status="in_progress",
            project=self.project,
            created_by=self.admin_user
        )

       
        self.task1.assigned_to.add(self.manager_user)
        self.task2.assigned_to.add(self.manager_user)

# يتأكد إن الأدمن يقدر يشوف البيانات العامة للوحة التحكم"

    def test_admin_dashboard_view(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("users", response.data)
        self.assertIn("projects", response.data)
        self.assertIn("tasks", response.data)

# يتأكد إن المستخدم يقدر يشوف مهامه فقط
    def test_user_task_dashboard_view(self):
        
        url = reverse("dashboard_user_task", args=[self.manager_user.id])
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("done", response.data)
        self.assertIn("in_progress", response.data)
        self.assertEqual(response.data["total_tasks"], 2)

#  يتأكد إن المستخدم يقدر يشوف المشاريع اللي مشارك فيها
    def test_user_projects_dashboard_view(self):

        url = reverse("dashboard_user", args=[self.manager_user.id])
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("projects", response.data)
        self.assertGreaterEqual(len(response.data["projects"]), 1)
        self.assertEqual(response.data["user"]["username"], "manager")

# يتأكد إن لازم يكون المستخدم مسجل دخول
    def test_dashboard_requires_authentication(self):
        
        self.client.force_authenticate(user=None)
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
