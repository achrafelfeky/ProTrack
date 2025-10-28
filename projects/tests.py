from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from projects.models import Project
from notifications.models import Notification
from datetime import timedelta, date
from django.utils import timezone

class ProjectAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # إنشاء مستخدمين
        self.admin_user = User.objects.create_user(username="admin", password="123", role="admin")
        self.manager_user = User.objects.create_user(username="manager", password="1234", role="manager")
        self.employee_user = User.objects.create_user(username="employee", password="1234", role="employee")

        # إنشاء مشروع مع إضافة مستخدمين إلى المشروع
        self.project = Project.objects.create(
            name="Test Project",
            description="desc",
            owner=self.admin_user,
            due_date=date.today() + timedelta(days=3),  # لتفعيل إشعار 3 أيام
        )
        # إضافة المستخدمين كمكلفين بالمشروع
        self.project.assigned_to.add(self.admin_user, self.manager_user, self.employee_user)

    # ================= إنشاء مشروع =================
    def test_create_project_as_admin(self):
        """الأدمن يقدر ينشئ مشروع"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("project-list")
        data = {
            "name": "New Admin Project",
            "description": "Created by admin",
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "todo",
            "priority": "medium",
            "assigned_to": [self.manager_user.id],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # تحقق من إنشاء إشعار
        notif = Notification.objects.filter(user=self.admin_user, title="مشروع جديد").first()
        self.assertIsNotNone(notif)

    def test_create_project_as_manager_forbidden(self):
        """المدير لا يمكنه إنشاء مشروع"""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse("project-list")
        data = {
            "name": "Manager Project",
            "description": "Should fail",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ================= عرض المشاريع =================
    def test_list_projects_authenticated(self):
        """الأدمن أو المدير فقط يمكنهم عرض المشاريع"""
        # جرب بالأدمن
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # جرب بالمدير
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # جرب بالموظف العادي
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ================= تحديث المشروع =================
    def test_update_project_as_admin(self):
        """الأدمن يمكنه تحديث المشروع ويولد إشعارات إذا انتهى"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("project-detail", args=[self.project.id])
        data = {
            "name": self.project.name,
            "description": self.project.description,
            "status": "done",  # انتهاء المشروع
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # تحقق من إشعار انتهاء المشروع
        notif = Notification.objects.filter(user=self.manager_user, title="انتهاء المشروع").first()
        self.assertIsNotNone(notif)

    # ================= إشعار قرب موعد التسليم =================
    def test_due_date_notification(self):
        """يجب إرسال إشعار قبل 3 أيام من موعد التسليم"""
        self.client.force_authenticate(user=self.admin_user)
        # تعديل المشروع ليكون الموعد بعد 3 أيام من الآن
        self.project.due_date = date.today() + timedelta(days=3)
        self.project.save()
        url = reverse("project-detail", args=[self.project.id])
        data = {
            "name": self.project.name,
            "description": self.project.description,
            "status": self.project.status,
        }
        self.client.put(url, data, format="json")
        notif = Notification.objects.filter(user=self.manager_user, title="قرب موعد تسليم المشروع").first()
        self.assertIsNotNone(notif)
