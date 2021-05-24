from django.urls import include, path

from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('jwt/token', TokenObtainPairView.as_view(), name='create_tokens'),
    path('jwt/refresh', TokenRefreshView.as_view(), name='refresh_token'),
    path('signup', views.signup_view, name='sign_up'),
    path('reset', views.reset_password_view, name='reset_password'),
    path('profile', views.profile_view, name='profile')
]
