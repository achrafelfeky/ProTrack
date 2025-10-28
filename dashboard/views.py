from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from projects.models import Project
from members.models import ProjectMember
from tasks.models import Task
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
from users.views import AdminAndManagerMixin
from rest_framework.views import APIView


# Dashboard ----------> admin and manager
@extend_schema(tags=["Dashboard"])
class DashboardView(AdminAndManagerMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = "dashboard_admin_manager"
        data = cache.get(cache_key)

        if not data:
            print("🔄 Cache MISS → Generating new dashboard data...")

            users = User.objects.all()
            members = ProjectMember.objects.all()

            task_done = Task.objects.filter(normal_status="done")
            task_in_progress = Task.objects.filter(status="in_progress")

            project_done = Project.objects.filter(status="done")
            project_in_progress = Project.objects.filter(status="in_progress")

            data = {
                "users": {
                    "count": users.count(),
                    "names": [user.username for user in users]
                },
                "members": {
                    "count": members.count(),
                    "members_info": [
                        {
                            "username": member.user.username,
                            "project": member.project.name,
                            "role": member.role
                        }
                        for member in members
                    ]
                },
                "tasks": {
                    "done_count": task_done.count(),
                    "done_titles": [task.title for task in task_done],
                    "in_progress_count": task_in_progress.count(),
                    "in_progress_titles": [task.title for task in task_in_progress],
                },
                "projects": {
                    "done_count": project_done.count(),
                    "done_titles": [project.name for project in project_done],
                    "in_progress_count": project_in_progress.count(),
                    "in_progress_titles": [task.title for task in task_in_progress],
                },
            }

            # Add Cache
            cache.set(cache_key, data, timeout=600)
        else:
            print("✅ Cache HIT → Returning cached dashboard data.")

        return Response(data)




# Dashboard ----------> user --------> Tasks
@extend_schema(tags=["Dashboard Tasks"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Dashboard_User_Task(request, pk):
    cache_key = f"user_{pk}_dashboard_tasks"
    data = cache.get(cache_key)

    if not data:
        print("🔄 Cache MISS → Generating user task dashboard...")

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "المستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)

        tasks = Task.objects.filter(assigned_to=user)

        def get_task_info(status_name):
            filtered_tasks = tasks.filter(status=status_name)
            return {
                "count": filtered_tasks.count(),
                "titles": [task.title for task in filtered_tasks]
            }

        data = {
            "todo": get_task_info("todo"),
            "in_progress": get_task_info("in_progress"),
            "pending_approval": get_task_info("pending_approval"),
            "returned": get_task_info("returned"),
            "approved": get_task_info("approved"),
            "rejected": get_task_info("rejected"),
            "done": get_task_info("done"),
            "total_tasks": tasks.count()
        }
        # Add Cache
        cache.set(cache_key, data, timeout=600)
    else:
        print("✅ Cache HIT → Returning cached user task dashboard.")

    return Response(data)



# Dashboard ----------> user ----------> data
@extend_schema(tags=["Dashboard User"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UserProjectsDashboard(request, pk):
    cache_key = f"user_{pk}_projects_dashboard"
    data = cache.get(cache_key)

    if not data:
        print("🔄 Cache MISS → Generating user project dashboard...")

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user_projects = ProjectMember.objects.filter(user=user).select_related('project')

        projects_data = []
        for membership in user_projects:
            project = membership.project
            projects_data.append({
                "project_id": project.id,
                "project_name": project.name,
                "status": project.status,
                "due_date": project.due_date,
            })

        data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": getattr(user, "role", "User")
            },
            "projects": projects_data
        }
        # Add Cache
        cache.set(cache_key, data, timeout=600)
    else:
        print("✅ Cache HIT → Returning cached user project dashboard.")

    return Response(data)
