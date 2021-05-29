from django.urls import include, path

from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('login', TokenObtainPairView.as_view(), name='create_tokens'),
    path('jwt/refresh', TokenRefreshView.as_view(), name='refresh_token'),
    path('signup', views.signup_view, name='sign_up'),
    path('reset', views.reset_password_view, name='reset_password'),
    path('profile', views.profile_view, name='profile'),
    path('friends/add/<str:friend_username>', views.add_friend, name='profile'),
    path('friends/search/<str:query>', views.search_friend, name='profile'),
    path('friends/delete/<str:friend_id>', views.delete_friend, name='profile')
]
