from urllib.parse import urlparse, parse_qs, urlunparse

from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework import views
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
from rest_framework.response import Response
from rest_framework.serializers import ValidationError as APIValidationError
from rest_framework.pagination import PageNumberPagination

from api.schema import MiddlewareAPISchema
from core.models import Source
from core.mock.persons import PersonsMock


MOCKS = {
    "persons": PersonsMock()
}


class ListEntities(views.APIView):
    """
    This endpoint returns objects of the specified entity for the specified source.
    Values for the *source* and *entity* parameters can be acquired from the sources endpoint.
    If you encounter "unprocessable entity" errors
    be sure to check the sources endpoint whether the requested source supports the requested entity.

    ## Response body

    **count**: The total amount of entities available from the source

    **next**: A link to the next page of results

    **previous**: A link to the previous page of results, this property may always be null for some sources

    **results**: A list of objects representing the entities. Properties vary depending on requested entity.
    """

    schema = MiddlewareAPISchema()

    @staticmethod
    def _validate_cursor(cursor):
        cursor_validator = RegexValidator("page\|\d\|\d")
        try:
            cursor_validator(cursor)
        except ValidationError:
            raise APIValidationError(detail="Invalid cursor")

    @staticmethod
    def _convert_to_cursor_response(response, page_size):
        for link_key in ["next", "previous"]:
            if not response.data[link_key]:
                continue
            link = urlparse(response.data[link_key])
            params = parse_qs(link.query)
            link_page_param = params.get("page", [])
            link_page_number = link_page_param[0] if len(link_page_param) else 1
            link = link._replace(query=f"cursor=page|{link_page_number}|{page_size}")
            response.data[link_key] = urlunparse(link)
        return response

    def _get_paginated_response(self, request, cursor, data):
        # Monkey patch the request to fool the pagination class into page pagination
        request.GET._mutable = True
        if not cursor.startswith("page"):
            raise APIValidationError(detail="Invalid cursor")
        pagination_type, page_number, page_size = cursor.split("|")
        request.GET.update({
            "page": page_number,
            "page_size": page_size
        })
        # Render the standard paginated response
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "page_size"
        page_data = paginator.paginate_queryset(data, request, view=self)
        response = paginator.get_paginated_response(data=page_data)
        # Modify the next and previous URL's to use our own cursor format
        return self._convert_to_cursor_response(response, page_size)

    def get(self, request, *args, **kwargs):
        # Read and validate input params
        # Pagination cursor
        cursor = request.GET.get("cursor", "page|1|100")
        self._validate_cursor(cursor)
        # Path variables
        source = get_object_or_404(Source, slug=kwargs.get("source", None))
        entity = kwargs.get("entity", None)
        if not source.is_allowed(entity):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY)
        # Return paginated results by parsing the cursor
        return self._get_paginated_response(request, cursor, MOCKS[entity].data)
