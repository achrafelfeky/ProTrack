from django.shortcuts import render
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from activitylog.views import ActivityLogger
from rest_framework.exceptions import PermissionDenied
from tasks.models import Task

# Create User
class RegisterUser(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()


            ActivityLogger.log(
                user=user,
                action=f"New user registered: {user.username}",
                instance=None
            )

            return Response(
                {"msg": "User created successfully", "user": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Login User -------> Create Refresh and Access Tokens
class LoginUser(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            return Response({
                "msg": "تم تسجيل الدخول بنجاح",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get All Users
class GetUsers(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Admin Only
class AdminOnlyMixin:
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if not user.is_authenticated or user.role != 'admin':
            raise PermissionDenied("Admins only")

# Adnin and Manager and assigned_to -----------> Tasks
class AdminManagerOrAssignedStatusOnlyMixin:
    def check_permissions_for_instance(self, obj):
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Not authenticated")

        if user.role in ['admin', 'manager']:
            return "full_access"

        if obj and user in obj.assigned_to.all():
            return "status_only"

        raise PermissionDenied("Access denied: Admin, Manager, or Assigned user only")

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        access_level = self.check_permissions_for_instance(obj)


        if access_level == "status_only":
            allowed_fields = {'status'}
            data = {field: value for field, value in request.data.items() if field in allowed_fields}

 
            if not data:
                raise PermissionDenied("You can only update the task status.")
            request._full_data = data  


        return super().update(request, *args, **{**kwargs, "partial": True})

# Adnin and Manager and assigned_to -----------> Comment
class CommentPermissionMixin:
    def check_comment_permission(self, obj, method):
        user = self.request.user


        if user.role in ['admin', 'manager']:
            return True


        if method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != user:
                raise PermissionDenied("You can only modify or delete your own comments.")
            return True


        if method in ['GET', 'HEAD', 'OPTIONS']:
 
            if obj.user == user or user in obj.task.assigned_to.all():
                return True
            raise PermissionDenied("You are not allowed to view this comment.")


        raise PermissionDenied("You don't have permission to perform this action.")

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied("Authentication required.")


        try:
            obj = self.get_object()
        except Exception:
            obj = None  


        if obj:
            self.check_comment_permission(obj, request.method)

# Adnin and Created By
class AdminAndManagerMixin:
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied("سجل دخول من فضلك")
        
        if user.role != 'admin':
            raise PermissionDenied("غير مسموح لك")
        
        # if user != Task.created_by:
        #     raise PermissionDenied("غير مسموح لك ")

