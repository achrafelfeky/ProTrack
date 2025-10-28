from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from projects.models import Project
from .models import ProjectMember
from notifications.models import Notification


class ProjectMemberAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()


        self.admin_user = User.objects.create_user(
            username='admin', password='admin123', role='admin'
        )
        self.normal_user = User.objects.create_user(
            username='user', password='user123', role='member'
        )


        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.admin_user
        )


        self.members_url = reverse('member-list')

# "يتأكد إن الأدمن يقدر يضيف عضو للمشروع
    def test_admin_can_add_member(self):

        self.client.force_authenticate(user=self.admin_user)

        data = {
            "user": self.normal_user.id,
            "project": self.project.id,
            "role": "member"
        }

        response = self.client.post(self.members_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProjectMember.objects.filter(user=self.normal_user, project=self.project).exists())


        notif = Notification.objects.filter(user=self.normal_user).first()
        self.assertIsNotNone(notif)
        self.assertIn("تمت إضافتك", notif.title)

    def test_non_admin_cannot_add_member(self):
        """يتأكد إن المستخدم العادي ميتقدرش يضيف عضو"""
        self.client.force_authenticate(user=self.normal_user)

        data = {
            "user": self.normal_user.id,
            "project": self.project.id,
            "role": "member"
        }

        response = self.client.post(self.members_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_members_admin_only(self):
        """يتأكد إن الأدمن فقط يقدر يشوف الأعضاء"""
        ProjectMember.objects.create(user=self.normal_user, project=self.project, role='member')


        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_member_admin_only(self):
        """يتأكد إن الأدمن فقط يقدر يحذف عضو"""
        member = ProjectMember.objects.create(user=self.normal_user, project=self.project, role='member')
        url = reverse('member-detail', args=[member.id])


        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
