from django.urls import path, include
from rest_framework.routers import DefaultRouter
from activitylog.views import AuditLogViewSet


router = DefaultRouter()
router.register('activity', AuditLogViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),

]
