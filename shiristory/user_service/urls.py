from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='sign up'),
    path('checkLoginStatus', views.testLoginView, name='check login status'),
    # path('jwt/token/', obtain_jwt_token),
    # path('jwt/token/verify/', verify_jwt_token),
    # path('jwt/token/refresh/', refresh_jwt_token),
    # path('<str:group_id>/info/', views.get_group_info, name='Get Group Info'),
]