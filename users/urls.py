from django.urls import path
from django.http import HttpResponse
from .views import RegisterUser, LoginUser, GetUsers

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('get/', GetUsers.as_view(), name='get'),
]
