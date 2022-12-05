from collections import OrderedDict

from django.test import TestCase

from core.constants import PaginationTypes, AuthenticationTypes
from core.proxy import SourceMultipleResourcesProxy
from core.mock.persons import PersonsMock


class TestSourceMultipleResourcesProxy(TestCase):

    base = {
        "url": "http://localhost:8080",
        "parameters": {
            "test": "param"
        },
        "headers": {},
        "resources": {
            "persons": {
                "user": {
                    "url": "/mocks/entity/user",
                    "resource_id": "$.external_id",
                    "results_path": "$.results"
                }
            }
        }
    }
    endpoints = {
        "persons": {
            "url": "/mocks/entity/partial-persons",
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
        self.proxy = SourceMultipleResourcesProxy(self.base, self.endpoints, self.auth, self.pagination)
        self.person_mock = PersonsMock()

    def test_extract_resource_identifiers(self):
        partial_response = self.client.get("/mocks/entity/partial-persons/")
        identifiers_1 = self.proxy.extract_resource_identifiers(
            partial_response,
            "offset|0|2",
            self.base["resources"]["persons"]["user"]
        )
        self.assertEqual(identifiers_1, [14949, 14774])
        identifiers_2 = self.proxy.extract_resource_identifiers(
            partial_response,
            "offset|2|2",
            self.base["resources"]["persons"]["user"]
        )
        self.assertEqual(identifiers_2, [14944, 14546])

    def test_build_detail_request(self):
        user_request = self.proxy.build_resource_request(self.base["resources"]["persons"]["user"], 14949)
        self.assertEqual(user_request.method, "GET")
        self.assertEqual(user_request.url, "http://localhost:8080/mocks/entity/user/14949")
        self.assertEqual(user_request.params, {
            "test": "param"
        })
        self.assertEqual(user_request.headers["api-key"], "access")

    def test_fetch(self):
        response = self.proxy.fetch("persons", "offset|0|100")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 200)
        self.assertEqual(data["next"], "http://localhost:8080/mocks/entity/partial-persons/?page=2&test=param")
        self.assertIsNone(data["previous"])
        self.assertEqual(len(data["results"]), 100)
        reference_person = self.person_mock.build_person("reference")
        for result in data["results"]:
            self.assertIsInstance(result, dict)
            self.assertIn("user", result, "Expected an user object to get added to the 'partial person' entity")
            self.assertIsInstance(result["user"], dict)
            self.assertTrue(
                all(key in result["user"] for key in reference_person),
                "Expected user object to contain keys that give extra information about 'partial person'"
            )
            self.assertEqual(
                result["user"]["email"],
                self.person_mock.build_email(result["name"]),
                "Expected the user resource to contain email addresses"
            )
