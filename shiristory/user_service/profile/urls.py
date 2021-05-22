from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='get-profile-details'),
    path('update/nickname', views.nickname_update_view, name='update-profile-nickname'),
    path('update/bio', views.bio_update_view, name='update-profile-bio'),
    path('update/image', views.image_update_view, name='update-profile-image'),
]
