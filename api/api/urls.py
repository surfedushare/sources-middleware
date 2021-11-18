from django.contrib import admin
from django.urls import path, include

from core.views import ListSources, ListEntities

api_urlpatterns = [
    path("sources", ListSources.as_view()),
    path("entities/<str:entity>/<str:source>", ListEntities.as_view())
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_urlpatterns, "v1",))),
]
