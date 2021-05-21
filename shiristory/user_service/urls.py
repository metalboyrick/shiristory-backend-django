from django.urls import path

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='sign up'),
    path('logout', views.logout_view, name='logout'),
    path('checkLoginStatus', views.testLoginView, name='check login status'),
    path('jwt/token', TokenObtainPairView.as_view()),
    path('jwt/token/refresh', TokenRefreshView.as_view()),
    # path('<str:group_id>/info/', views.get_group_info, name='Get Group Info'),
]