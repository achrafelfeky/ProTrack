from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from rest_framework.exceptions import PermissionDenied
from users.views import AdminOnlyMixin, RegisterUser, LoginUser, GetUsers
from rest_framework.response import Response
class UserAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # مستخدمين
        self.admin_user = User.objects.create_user(username="admin", password="123", role="admin")
        self.manager_user = User.objects.create_user(username="manager", password="1234", role="manager")
        self.employee_user = User.objects.create_user(username="employee", password="1234", role="member")

    # ===================== تسجيل مستخدم جديد =====================
    def test_register_user_success(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "role": "member"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="newuser").exists(), True)

    # ===================== تسجيل الدخول =====================
    def test_login_user_success(self):
        url = reverse("login")
        data = {"username": "admin", "password": "123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_login_user_fail_wrong_password(self):
        url = reverse("login")
        data = {"username": "admin", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ===================== عرض المستخدمين =====================
    def test_get_users_authenticated(self):
        url = reverse("get")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 3)

    def test_get_users_unauthenticated(self):
        url = reverse("get")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # ===================== AdminOnlyMixin =====================
    # def test_admin_only_blocks_non_admin(self):
    #     class DummyView(AdminOnlyMixin, RegisterUser):
    #         def get(self, request, *args, **kwargs):
    #             return Response({"ok": True})

    #     view = DummyView.as_view()
    #     self.client.force_authenticate(user=self.manager_user)
    #     url = reverse("register")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 403)

    # def test_admin_only_allows_admin(self):
    #     class DummyView(AdminOnlyMixin, RegisterUser):
    #         def get(self, request, *args, **kwargs):
    #             return Response({"ok": True})

    #     view = DummyView.as_view()
    #     self.client.force_authenticate(user=self.admin_user)
    #     url = reverse("register")
    #     response = self.client.get(url)
    #     self.assertTrue(True)  
