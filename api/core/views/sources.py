from rest_framework import generics

from core.models import Source, SourceSerializer


class ListSources(generics.ListAPIView):
    """
    TODO: Documentation string ...
    """

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
