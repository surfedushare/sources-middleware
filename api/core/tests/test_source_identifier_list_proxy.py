from collections import OrderedDict

from django.test import TestCase

from core.constants import PaginationTypes, AuthenticationTypes
from core.proxy import SourceIdentifierListProxy


class TestSourceIdentifierListProxy(TestCase):

    base = {
        "url": "http://localhost:8080",
        "parameters": {
            "test": "param"
        },
        "headers": {},
        "identifier_list": {
            "identifier_path": "$.id"
        }
    }
    endpoints = {
        "projects": {
            "url": "/mocks/entity/project-ids",
            "extractor": "MockProjectExtractProcessor"
        }
    }
    auth = {
        "type": AuthenticationTypes.API_KEY_HEADER,
        "token": "access"
    }
    pagination = {
        "type": PaginationTypes.OFFSET,
        "parameters": OrderedDict({
            "offset": 0,
            "size": 100
        })
    }

    def setUp(self):
        super().setUp()
        self.proxy = SourceIdentifierListProxy(self.base, self.endpoints, self.auth, self.pagination)

    def test_extract_identifiers(self):
        identifiers_response = self.client.get("/mocks/entity/project-ids/")
        identifiers_1 = self.proxy.extract_identifiers(identifiers_response, "offset|0|2")
        self.assertEqual(
            identifiers_1["identifiers"],
            ["b8c6aa6611e89f6f57545991e40f782e", "e78db0ee041b358c125c39abfa60da9b"]
        )
        self.assertEqual(identifiers_1["count"], 200)
        self.assertEqual(identifiers_1["pagination"], {
            "offset": 0,
            "size": 2
        })
        identifiers_2 = self.proxy.extract_identifiers(identifiers_response, "offset|2|2")
        self.assertEqual(
            identifiers_2["identifiers"],
            ["ed9d32d9000229b47d6acb8ac1dad9a2", "ed13bb012325d265868e5b8060db9713"]
        )
        self.assertEqual(identifiers_2["count"], 200)
        self.assertEqual(identifiers_2["pagination"], {
            "offset": 2,
            "size": 2
        })

    def test_build_detail_request(self):
        projects_request = self.proxy.build_detail_request("projects", "b8c6aa6611e89f6f57545991e40f782e")
        self.assertEqual(projects_request.method, "GET")
        self.assertEqual(
            projects_request.url,
            "http://localhost:8080/mocks/entity/project-ids/b8c6aa6611e89f6f57545991e40f782e"
        )
        self.assertEqual(projects_request.params, {
            "test": "param"
        })
        self.assertEqual(projects_request.headers["api-key"], "access")

    def test_fetch(self):
        response = self.proxy.fetch("projects", "offset|0|100")
        data = response.json()
        self.assertEqual(data["count"], 200)
        self.assertEqual(data["pagination"], {
            "offset": 0,
            "size": 100
        })
        self.assertEqual(len(data["results"]), 100)
