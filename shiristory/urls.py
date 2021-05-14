from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('user/', include('shiristory.user_service.urls')),
    path('story/', include('shiristory.story_service.urls')),
    path('timeline/', include('shiristory.timeline_service.urls')),
    path('admin/', admin.site.urls),
]