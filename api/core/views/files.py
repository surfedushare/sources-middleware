from sentry_sdk import capture_message

from django.conf import settings
from django.shortcuts import get_object_or_404, Http404
from django.http import StreamingHttpResponse, HttpResponse
from rest_framework import views
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from api.schema import MiddlewareAPISchema
from core.models import Source
from core.proxy import SourceFileProxy


class ProxyFiles(views.APIView):
    """
    This endpoint returns a streaming response for the file at *file_path*.
    Exactly which *file_path* has to be given depends on the *source*.
    The endpoint tries to be conservative as to which files it proxies for security reasons.

    ## Response

    The return type for this endpoint is indicated as "string", but in truth this endpoint will stream the file.
    This makes it possible to use the file directly as part of HTML src attributes.

    Also note that if errors occur these errors are returned in JSON format and not as a streaming file.
    Check the status code of the response to see if any errors occurred and handle the response accordingly.
    """

    schema = MiddlewareAPISchema()
    permission_classes = (AllowAny,)

    def validate_request(self, request, view_kwargs):
        # Read and validate input params
        file_path = view_kwargs.get("file_path", None)
        if ".." in file_path:
            raise ValidationError("Relative paths are not allowed when proxying files")
        # Load the source and its proxy
        source = get_object_or_404(Source, slug=view_kwargs.get("source", None))
        if source.slug not in settings.SOURCES:
            raise Http404(f"Source implementation '{source.slug}' not found in settings")
        # Build the correct proxy class
        source_proxy = SourceFileProxy(**settings.SOURCES[source.slug])
        return source, source_proxy, file_path

    def fetch_source_response(self, request, *args, **kwargs):
        source, source_proxy, file_path = self.validate_request(request, kwargs)
        # See if requested entity can be processed
        if not source.is_allowed("files") or not source_proxy.is_implemented("files"):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY)
        # Return paginated results by parsing the cursor
        source_response = source_proxy.fetch("files", path=file_path)
        if not source_response.status_code == HTTP_200_OK:
            message = f"Source fetch responded with {source_response.status_code}: {source_response.reason}"
            capture_message(message, level="warning")
            return Response(data={"detail": message}, status=source_response.status_code), source_response.status_code
        return source_response, 0

    def get(self, request, *args, **kwargs):
        source_response, error_code = self.fetch_source_response(request, *args, **kwargs)
        if error_code:
            return source_response
        return StreamingHttpResponse(
            source_response.raw,
            content_type=source_response.headers.get('content-type'),
            status=source_response.status_code,
            reason=source_response.reason
        )

    def head(self, request, *args, **kwargs):
        """
        HEAD requests are made by the harvester.
        However Pure doesn't support HEAD request.
        This method emulates a HEAD request by ignoring the response body.
        """
        source_response, error_code = self.fetch_source_response(request, *args, **kwargs)
        if error_code:
            return source_response
        return HttpResponse(
            "",
            content_type=source_response.headers.get('content-type'),
            status=source_response.status_code,
            reason=source_response.reason
        )
