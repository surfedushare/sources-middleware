from collections import OrderedDict

from django.test import TestCase

from core.constants import PaginationTypes, AuthenticationTypes
from core.proxy import SourceFileProxy


class TestSourceProxy(TestCase):

    base = {
        "url": "http://localhost:8080",
        "parameters": {
            "test": "param"
        },
        "headers": {}
    }
    endpoints = {
        "files": {
            "url": "/mocks/files/{path}",
            "extractor": None
        }
    }
    auth = {
        "type": AuthenticationTypes.API_KEY_HEADER,
        "header": "api-key",
        "token": "access"
    }
    pagination = {
        "type": PaginationTypes.PAGE,
        "parameters": OrderedDict({
            "page": 0,
            "size": 100
        })
    }

    def setUp(self):
        super().setUp()
        self.proxy = SourceFileProxy(self.base, self.endpoints, self.auth, self.pagination)

    def test_init(self):
        self.assertEqual(self.proxy.base, self.base)
        self.assertEqual(self.proxy.endpoints, self.endpoints)
        self.assertEqual(self.proxy.auth, self.auth)
        self.assertEqual(self.proxy.pagination, self.pagination)
        self.assertTrue(
            self.proxy.is_stream,
            "Expected FileProxy to always stream its responses regardless of init arguments"
        )

    def test_build_request_path(self):
        file_request = self.proxy.build_request("files", path="path/to/file.pdf")
        self.assertEqual(file_request.method, "GET")
        self.assertEqual(file_request.url, "http://localhost:8080/mocks/files/path/to/file.pdf")
        self.assertEqual(file_request.params, {"test": "param"})
        self.assertEqual(file_request.headers["api-key"], "access")
