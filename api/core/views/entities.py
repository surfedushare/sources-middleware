from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY
from rest_framework.response import Response

from core.models import Source


class ListEntities(views.APIView):
    """
    TODO: Documentation string ...
    """

    def get(self, request, *args, **kwargs):
        source = get_object_or_404(Source, slug=kwargs.get("source", None))
        entity = kwargs.get("entity", None)
        if not source.is_allowed(entity):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data=[], status=HTTP_200_OK)
