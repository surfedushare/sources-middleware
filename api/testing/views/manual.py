from django.shortcuts import Http404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from testing.models import ManualPerson, ManualProject


class ManualEntityAPIView(APIView):

    permission_classes = (AllowAny,)

    @staticmethod
    def get_objects(manual_id, entity):
        match entity:
            case "persons":
                queryset = ManualPerson.objects.filter(source=manual_id)
            case "projects":
                queryset = ManualProject.objects.filter(source=manual_id)
            case _:
                raise Http404()
        return [instance.properties for instance in queryset]

    def get(self, request, manual_id, entity):
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "page_size"
        objects = self.get_objects(manual_id, entity)
        page_data = paginator.paginate_queryset(objects, request, view=self)
        return paginator.get_paginated_response(data=page_data)
