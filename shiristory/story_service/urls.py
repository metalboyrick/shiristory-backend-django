from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:group_id>/info/', views.get_group_info, name='Get Group Info'),

    # Admin activities
    path('<str:group_id>/admin/', views.edit_admin, name='Edit admins'),
    path('<str:group_id>/admin/info/', views.edit_group_info, name='Edit Group Info'),
    path('<str:group_id>/admin/member/', views.edit_member, name='Edit members')


]
