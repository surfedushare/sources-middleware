from collections import OrderedDict

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.constants import PaginationTypes, AuthenticationTypes
from core.proxy import SourceProxy


class TestSourceProxy(TestCase):

    base = {
        "url": "http://localhost:9000",
        "parameters": {
            "test": "param"
        }
    }
    endpoints = {
        "persons": "/api/v1/persons",
        "projects": "/api/v1/projects"
    }
    auth = {
        "type": AuthenticationTypes.API_KEY_HEADER,
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
        self.proxy = SourceProxy(self.base, self.endpoints, self.auth, self.pagination)

    @classmethod
    def build_pagination_proxies(cls):
        pagination_parameters = {
            PaginationTypes.PAGE: {
                "page": 0,
                "size": 100
            },
            PaginationTypes.OFFSET: {
                "offset": 0,
                "size": 100
            },
            PaginationTypes.CURSOR: {
                "cursor": None
            }
        }
        return {
            pagination_type: SourceProxy(
                cls.base,
                cls.endpoints,
                cls.auth,
                {
                    "type": pagination_type,
                    "parameters": pagination_parameters[pagination_type]
                }
            )
            for pagination_type in PaginationTypes
        }

    def test_validate_cursor(self):
        cursors = {
            PaginationTypes.PAGE: "page|0|10",
            PaginationTypes.OFFSET: "offset|100|100",
            PaginationTypes.CURSOR: "standard_cursor"
        }
        cursor_defaults = {
            PaginationTypes.PAGE: "page|0|100",
            PaginationTypes.OFFSET: "offset|0|100",
            PaginationTypes.CURSOR: None
        }
        proxies = self.build_pagination_proxies()
        for pagination_proxy, proxy in proxies.items():
            self.assertEqual(
                proxy.validate_cursor(None),
                cursor_defaults[pagination_proxy],
                "A None cursor should return the cursor default based on default pagination parameters"
            )
            for pagination_cursor, cursor in cursors.items():
                if pagination_proxy == PaginationTypes.CURSOR:
                    self.assertEqual(proxy.validate_cursor(cursor), cursor)
                elif pagination_proxy == pagination_cursor:
                    self.assertEqual(proxy.validate_cursor(cursor), cursor)
                else:
                    try:
                        proxy.validate_cursor(cursor)
                        self.fail(
                            f"Proxy with pagination {pagination_proxy} did not raise "
                            f"when processing a {pagination_cursor} cursor"
                        )
                    except ValidationError:
                        pass

    def test_build_request_default(self):
        persons_request = self.proxy.build_request("persons")
        self.assertEqual(persons_request.method, "GET")
        self.assertEqual(persons_request.url, "http://localhost:9000/api/v1/persons")
        self.assertEqual(persons_request.params, {
            "test": "param"
        })
        self.assertEqual(persons_request.headers["api-key"], "access")
        projects_request = self.proxy.build_request("projects")
        self.assertEqual(projects_request.method, "GET")
        self.assertEqual(projects_request.url, "http://localhost:9000/api/v1/projects")
        self.assertEqual(projects_request.params, {
            "test": "param"
        })
        self.assertEqual(projects_request.headers["api-key"], "access")

    def test_build_request_cursor(self):
        persons_request = self.proxy.build_request("persons", "page|2|100")
        self.assertEqual(persons_request.method, "GET")
        self.assertEqual(persons_request.url, "http://localhost:9000/api/v1/persons")
        self.assertEqual(persons_request.params, {
            "test": "param",
            "page": 2,
            "size": 100
        })
        self.assertEqual(persons_request.headers["api-key"], "access")
        projects_request = self.proxy.build_request("projects", "page|2|100")
        self.assertEqual(projects_request.method, "GET")
        self.assertEqual(projects_request.url, "http://localhost:9000/api/v1/projects")
        self.assertEqual(projects_request.params, {
            "test": "param",
            "page": 2,
            "size": 100
        })
        self.assertEqual(projects_request.headers["api-key"], "access")
