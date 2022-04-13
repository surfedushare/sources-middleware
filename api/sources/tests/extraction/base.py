import os
import json
from unittest.mock import Mock
from requests import Response

from django.conf import settings
from django.test import TestCase

from core.proxy import SourceProxy


class ExtractorTestCase(TestCase):

    source = None
    entity = None

    @classmethod
    def setUpClass(cls):
        assert cls.source and cls.entity, "ExtractorTestCase is missing a source or entity attribute"
        super().setUpClass()
        json_path = os.path.join(settings.BASE_DIR, "sources", "fixtures", cls.source, f"{cls.entity}.json")
        with open(json_path) as json_file:
            cls.response = Mock(Response)
            cls.response.json = Mock(return_value=json.load(json_file))
        cls.source_proxy = SourceProxy(**settings.SOURCES[cls.source])
        cls.extractor = cls.source_proxy.build_extractor(cls.entity, cls.response)
        cls.results = list(cls.extractor.extract(cls.extractor.CONTENT_TYPE, cls.extractor.data))
