from collections import OrderedDict

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.constants import PaginationTypes, AuthenticationTypes
from core.proxy import SourceProxy


class TestSourceProxy(TestCase):

    base = {
        "url": "http://localhost:8080",
        "parameters": {
            "test": "param"
        },
        "headers": {}
    }
    endpoints = {
        "persons": {
            "url": "/mocks/entity/persons/",
            "extractor": "MockPersonExtractProcessor"
        },
        "projects": {
            "url": "/mocks/entity/projects/",
            "extractor": "MockProjectExtractProcessor"
        }
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

    def test_validate_cursor_no_pagination(self):
        self.proxy.pagination = {}
        self.assertIsNone(self.proxy.validate_cursor(None))
        self.assertIsNone(self.proxy.validate_cursor("page|0|10"))
        self.assertIsNone(self.proxy.validate_cursor("offset|100|100"))
        self.assertIsNone(self.proxy.validate_cursor("standard_cursor"))

    def test_build_request_default(self):
        persons_request = self.proxy.build_request("persons")
        self.assertEqual(persons_request.method, "GET")
        self.assertEqual(persons_request.url, "http://localhost:8080/mocks/entity/persons/")
        self.assertEqual(persons_request.params, {
            "test": "param"
        })
        self.assertEqual(persons_request.headers["api-key"], "access")
        projects_request = self.proxy.build_request("projects")
        self.assertEqual(projects_request.method, "GET")
        self.assertEqual(projects_request.url, "http://localhost:8080/mocks/entity/projects/")
        self.assertEqual(projects_request.params, {
            "test": "param"
        })
        self.assertEqual(projects_request.headers["api-key"], "access")

    def test_build_request_cursor(self):
        persons_request = self.proxy.build_request("persons", "page|2|100")
        self.assertEqual(persons_request.method, "GET")
        self.assertEqual(persons_request.url, "http://localhost:8080/mocks/entity/persons/")
        self.assertEqual(persons_request.params, {
            "test": "param",
            "page": 2,
            "size": 100
        })
        self.assertEqual(persons_request.headers["api-key"], "access")
        projects_request = self.proxy.build_request("projects", "page|2|100")
        self.assertEqual(projects_request.method, "GET")
        self.assertEqual(projects_request.url, "http://localhost:8080/mocks/entity/projects/")
        self.assertEqual(projects_request.params, {
            "test": "param",
            "page": 2,
            "size": 100
        })
        self.assertEqual(projects_request.headers["api-key"], "access")

    def test_build_persons_extractor(self):
        persons_response = self.client.get("/mocks/entity/persons/")
        persons_extractor = self.proxy.build_extractor("persons", persons_response)
        self.assertEqual(persons_extractor.config.entity, "persons")
        self.assertIn("objective", persons_extractor.config)
        persons_objective = persons_extractor.config.objective
        self.assertEqual(persons_objective["@"], "$.results")
        self.assertEqual(persons_extractor.response, persons_response)

    def test_build_projects_extractor(self):
        projects_response = self.client.get("/mocks/entity/projects/")
        projects_extractor = self.proxy.build_extractor("projects", projects_response)
        self.assertEqual(projects_extractor.config.entity, "projects")
        self.assertIn("objective", projects_extractor.config)
        projects_objective = projects_extractor.config.objective
        self.assertEqual(projects_objective["@"], "$.results")
        self.assertEqual(projects_extractor.response, projects_response)
