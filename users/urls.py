from django.urls import path
from .views import RegisterUser, LoginUser, GetUsers, RefreshTokenView, LogoutView

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('get/', GetUsers.as_view(), name='get'),
    path("token/refresh/", RefreshTokenView.as_view(), name="custom_token_refresh"),
    path("logout/", LogoutView.as_view(), name="custom_token_logout"),
]
