from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddProject


router = DefaultRouter()
router.register('project', AddProject, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
