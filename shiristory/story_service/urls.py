from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:group_id>/info/', views.get_group_info, name='Get Group Info')
]
