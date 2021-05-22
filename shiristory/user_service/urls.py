from django.urls import include, path

from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='sign-up'),
    path('logout', views.logout_view, name='logout'),
    path('whoami', views.whoami_view, name='check-login-status'),
    path('reset', views.reset_password_view, name='reset-password'),
    path('jwt/refresh', TokenRefreshView.as_view(), name='refresh-token'),
    path('profile/', include('shiristory.user_service.profile.urls'))
    # path('<str:group_id>/info/', views.get_group_info, name='Get Group Info'),
]