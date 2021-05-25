from django.urls import path

from . import views

urlpatterns = [
    path('view', views.index, name='index'),
    path('create', views.create, name='create'),
    path('<str:post_id>/comment', views.add_comment, name='add_comment'),
    path('<str:post_id>/like', views.like_post, name='like_post'),
    path('<str:post_id>/dislike', views.dislike_post, name='dislike_post'),
]