from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_group_list, name='Get group list'),
    path('upload' , views.upload_file, name='Upload files'),
    path('create/', views.create_group, name='Create new group'),
    path('<str:group_id>/info/', views.get_group_info, name='Get Group Info'),
    path('<str:group_id>/stories/', views.get_stories, name='Get stories'),

    # Admin activities
    path('<str:group_id>/admin/', views.edit_admin, name='Edit admins'),
    path('<str:group_id>/admin/info/', views.edit_group_info, name='Edit Group Info'),
    path('<str:group_id>/admin/member/', views.edit_member, name='Edit members')

]
