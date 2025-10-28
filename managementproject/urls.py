from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🧩 روابط التطبيقات
    path('api/users/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/members/', include('members.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/logs/', include('activitylog.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),

    # 📘 روابط Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
