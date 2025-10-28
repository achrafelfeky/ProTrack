from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # إنشاء مستخدمين
        self.user1 = User.objects.create_user(username='user1', password='pass1234', role='user')
        self.user2 = User.objects.create_user(username='user2', password='pass1234', role='user')

        # إشعارات للمستخدم الأول
        self.notification1 = Notification.objects.create(
            user=self.user1,
            title="Task Assigned",
            message="You have been assigned a new task"
        )
        self.notification2 = Notification.objects.create(
            user=self.user1,
            title="Project Update",
            message="Project status changed"
        )

        # روابط الـ API
        self.list_url = reverse('notifications')
        self.read_url = reverse('mark-as-read', kwargs={'pk': self.notification1.pk})

    def test_unauthenticated_user_cannot_access_notifications(self):
        """يجب على المستخدم غير المسجل الدخول أن يحصل على 401"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_see_their_notifications(self):
        """المستخدم المسجل يمكنه رؤية إشعاراته فقط"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user'], self.user1.id)

    def test_user_cannot_see_other_users_notifications(self):
        """المستخدم لا يمكنه رؤية إشعارات مستخدم آخر"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_mark_notification_as_read(self):
        """المستخدم يمكنه تحديد الإشعار كمقروء"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.read_url, {'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_user_cannot_mark_other_users_notification_as_read(self):
        """المستخدم لا يمكنه تعديل إشعار لا يخصه"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(self.read_url, {'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
