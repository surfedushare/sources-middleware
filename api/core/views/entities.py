from sentry_sdk import capture_message

from django.conf import settings
from django.shortcuts import get_object_or_404, Http404
from django.urls import reverse
from rest_framework import views
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK, HTTP_417_EXPECTATION_FAILED
from rest_framework.response import Response

from api.schema import MiddlewareAPISchema
from core.models import Source
from core.proxy import SourceProxy, SourceIdentifierListProxy, SourceMultipleResourcesProxy


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

    def validate_request(self, request, view_kwargs):
        # Read and validate input params
        entity = view_kwargs.get("entity", None)
        # Load the source and its proxy
        source = get_object_or_404(Source, slug=view_kwargs.get("source", None))
        if source.slug not in settings.SOURCES:
            raise Http404(f"Source implementation '{source.slug}' not found in settings")
        # Build the correct proxy class
        is_identifier_list_source = bool(settings.SOURCES[source.slug]["base"].get("identifier_list", None))
        is_multiple_resources_source = bool(settings.SOURCES[source.slug]["base"].get("resources", None)) and \
            entity in settings.SOURCES[source.slug]["base"]["resources"]
        if is_identifier_list_source or is_multiple_resources_source:
            assert is_identifier_list_source ^ is_multiple_resources_source, \
                "identifier_list and resources are mutually exclusive configurations"
            ProxyClass = SourceIdentifierListProxy if is_identifier_list_source else SourceMultipleResourcesProxy
        else:
            ProxyClass = SourceProxy
        source_proxy = ProxyClass(**settings.SOURCES[source.slug])
        # Validate cursor
        cursor = source_proxy.validate_cursor(request.GET.get("cursor", None))
        return source, source_proxy, entity, cursor

    def build_cursor_link(self, request, source, entity, cursor):
        if not cursor:
            return
        base_url = reverse("v1:entities", args=(entity, source.slug))
        return f"{request.build_absolute_uri(base_url)}?cursor={cursor}"

    def get(self, request, *args, **kwargs):
        source, source_proxy, entity, cursor = self.validate_request(request, kwargs)
        # See if requested entity can be processed
        if not source.is_allowed(entity) or not source_proxy.is_implemented(entity):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY)
        # Return paginated results by parsing the cursor
        source_response = source_proxy.fetch(entity, cursor)
        if not source_response.status_code == HTTP_200_OK:
            message = f"Source responded with {source_response.status_code}: {source_response.reason}"
            capture_message(message, level="warning")
            return Response(
                data={"detail": message},
                status=HTTP_417_EXPECTATION_FAILED
            )
        source_extractor = source_proxy.build_extractor(entity, source_response)
        source_data = source_extractor.data
        return Response(data={
            "count": source_extractor.get_api_count(source_data),
            "next": self.build_cursor_link(
                request, source, entity,
                source_extractor.get_api_next_cursor(source_data)
            ),
            "previous": self.build_cursor_link(
                request, source, entity,
                source_extractor.get_api_previous_cursor(source_data)
            ),
            "results": source_extractor.extract(source_extractor.CONTENT_TYPE, source_data)
        })
