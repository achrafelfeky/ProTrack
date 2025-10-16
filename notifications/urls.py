from django.urls import path
from .views import NotificationListView, MarkAsReadView

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', MarkAsReadView.as_view(), name='mark-as-read'),
]
