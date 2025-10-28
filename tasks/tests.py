from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from projects.models import Project
from tasks.models import Task


class TaskAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()


        self.admin_user = User.objects.create_user(username="admin", password="123", role="admin")
        self.manager_user = User.objects.create_user(username="manager", password="1234", role="manager")
        self.employee_user = User.objects.create_user(username="employee", password="1234", role="employee")

        # إنشاء مشروع (Project)
        self.project = Project.objects.create(
            name="Test Project",
            description="desc",
            owner=self.admin_user,  
        )

        # إنشاء مهمة (Task)
        self.task = Task.objects.create(
            project=self.project,
            title="Test Task",
            description="Task desc",
            created_by=self.manager_user,
        )
        self.task.assigned_to.add(self.employee_user)

    # ========================= إنشاء مهمة =========================
    def test_create_task_as_admin(self):
        """الأدمن يقدر ينشئ مهمة"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("tasks-list")
        data = {
            "project": self.project.id,
            "title": "Admin Task",
            "description": "Created by admin",
            "assigned_to": [self.employee_user.id],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_as_manager(self):
        """المدير يقدر ينشئ مهمة"""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse("tasks-list")
        data = {
            "project": self.project.id,
            "title": "Manager Task",
            "description": "Created by manager",
            "assigned_to": [self.employee_user.id],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_as_employee_forbidden(self):
        """الموظف لا يمكنه إنشاء مهمة"""
        self.client.force_authenticate(user=self.employee_user)
        url = reverse("tasks-list")
        data = {
            "project": self.project.id,
            "title": "Employee Task",
            "description": "Should fail",
            "assigned_to": [self.employee_user.id],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========================= إرسال للموافقة =========================
    def test_submit_task_for_approval(self):
        """الموظف المكلف يرسل المهمة للموافقة"""
        self.client.force_authenticate(user=self.employee_user)
        self.task.status = "in_progress"
        self.task.save()

        url = reverse("submit_task", args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "pending_approval")

    # ========================= الموافقة على المهمة =========================
    def test_approve_task(self):
        """الأدمن يوافق على المهمة"""
        self.client.force_authenticate(user=self.admin_user)
        self.task.status = "pending_approval"
        self.task.save()

        url = reverse("approve_task", args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "approved")

    # ========================= رفض المهمة =========================
    def test_reject_task(self):
        """الأدمن يرفض المهمة"""
        self.client.force_authenticate(user=self.admin_user)
        self.task.status = "pending_approval"
        self.task.save()

        url = reverse("reject_task", args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "rejected")

    # ========================= إرجاع المهمة =========================
    def test_return_task(self):
        """المدير أو الأدمن يرجع المهمة"""
        self.client.force_authenticate(user=self.manager_user)
        self.task.status = "pending_approval"
        self.task.save()

        url = reverse("return_task", args=[self.task.id])
        data = {"due_date": "2025-12-31"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "returned")
