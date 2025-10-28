from django.urls import path
from . import views
from .views import DashboardView

urlpatterns = [
  path("dashboard/", DashboardView.as_view(), name="dashboard"),
  path('dashboard/task/<int:pk>/', views.Dashboard_User_Task, name='dashboard_user_task'),
  path('dashboard/<int:pk>/', views.UserProjectsDashboard, name='dashboard_user'),
]
