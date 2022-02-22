from rest_framework import generics

from api.schema import MiddlewareAPISchema
from core.models import Source, SourceSerializer


class ListSources(generics.ListAPIView):
    """
    This endpoint returns all available sources and indicates which entities are available per source.
    The endpoint returns an object per source. Properties are described in detail below.

    ## Response body

    **name**: The human readable name for the source

    **slug**: Pass this slug to the entities API endpoint to get entities for this source

    **entities**: An object indicating which entities are supported by the source.
    Keys in the object are the entity slugs that you can pass to the entities endpoint.
    Values are again objects,
    where the *is_available* property indicates if the entity can be retrieved through this API.
    The *allows_update* property indicates whether changes on the entity can be written back to the source.
    """

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    schema = MiddlewareAPISchema()
