from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

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
