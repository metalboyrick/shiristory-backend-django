from django.urls import path

from . import views

urlpatterns = [
    path('view', views.index, name='index'),
    path('create', views.create, name='create'),
]