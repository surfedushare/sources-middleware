from django.shortcuts import Http404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.mock.persons import PersonsMock
from core.mock.projects import ProjectsMock


MOCKS = {
    "persons": PersonsMock(),
    "projects": ProjectsMock()
}


class EntityMockAPIView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, entity):
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "page_size"
        page_data = paginator.paginate_queryset(MOCKS[entity].data, request, view=self)
        return paginator.get_paginated_response(data=page_data)


class EntityMockIdListAPIView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, entity=None):
        return Response([{"id": obj["external_id"]} for obj in MOCKS[entity].data])


class EntityMockDetailAPIView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, pk, entity=None):
        try:
            return Response(next((obj for obj in MOCKS[entity].data if obj["external_id"] == pk)))
        except StopIteration:
            raise Http404(f"Object with primary key not found: {pk}")
