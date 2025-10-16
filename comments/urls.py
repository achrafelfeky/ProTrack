from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Comment


router = DefaultRouter()
router.register('comment', Comment, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
