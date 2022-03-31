from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from api.views import health_check
from core.views import ListSources, ListEntities
from core.mock.views import EntityMockAPIView

api_urlpatterns = [
    path("sources/", ListSources.as_view()),
    path("entities/<str:entity>/<str:source>/", ListEntities.as_view())
]


api_description = """
An API that allows downloading all data from different repositories from one endpoint.

To authenticate with the API you either need to login to the admin (useful to use this interactive documentation).
Or you have to send an Authorization header with a value of "Token <your-api-token>" (recommended).
"""
schema_view = get_schema_view(
    title="Publinova Middleware API",
    description=api_description,
    patterns=api_urlpatterns,
    url="/api/v1/"
)
swagger_view = TemplateView.as_view(
    template_name='swagger/swagger-ui.html',
    extra_context={'schema_url': 'v1:openapi-schema'}
)
api_urlpatterns += [
    path('openapi/', schema_view, name='openapi-schema'),
    path('docs/', swagger_view, name='docs'),
]


urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_urlpatterns, "v1",))),
    path('mocks/entity/<str:entity>/', EntityMockAPIView.as_view())
]
