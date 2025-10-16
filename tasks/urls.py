from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubmitTaskForApproval, ApproveTask, RejectTask, ReturnTask, TasksProject


router = DefaultRouter()
router.register('tasks', TasksProject, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('task/<int:pk>/submit/', SubmitTaskForApproval.as_view(), name='submit_task'),
    path('task/<int:pk>/approve/', ApproveTask.as_view(), name='approve_task'),
    path('task/<int:pk>/reject/', RejectTask.as_view(), name='reject_task'),
    path('task/<int:pk>/return/', ReturnTask.as_view(), name='return_task'),
]
