from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectMemberViewSet


router = DefaultRouter()
router.register('member', ProjectMemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
]
