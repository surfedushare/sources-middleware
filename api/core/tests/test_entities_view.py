from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from core.models import Source


class TestEntitiesView(TestCase):

    @classmethod
    def setUpTestData(cls):
        Source.objects.create(name="Mock", slug="mock", entities={
            entity: {
                "is_available": True,
                "allows_update": False
            }
            for entity in settings.ENTITIES
        })
        cls.tester = User.objects.create(username="tester")

    def setUp(self):
        super().setUp()
        self.client.force_login(self.tester)

    def test_get_persons(self):
        response = self.client.get("/api/v1/entities/persons/mock/", headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 200)
        results = data.pop("results")
        self.assertEqual(len(results), 100)
        self.assertIsNone(data["previous"])
        self.assertEqual(data["next"], "http://testserver/api/v1/entities/persons/mock/?cursor=page|2|100")
        next_response = self.client.get(
            "/api/v1/entities/persons/mock/?cursor=page|2|100",
            headers={"content-type": "application/json"}
        )
        self.assertEqual(next_response.status_code, 200)
        next_data = next_response.json()
        self.assertEqual(next_data["count"], 200)
        next_results = next_data.pop("results")
        self.assertEqual(len(next_results), 100)
        self.assertEqual(next_data["previous"], "http://testserver/api/v1/entities/persons/mock/?cursor=page|1|100")
        self.assertIsNone(next_data["next"])

    def test_get_projects(self):
        response = self.client.get("/api/v1/entities/projects/mock/", headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 200)
        results = data.pop("results")
        self.assertEqual(len(results), 100)
        self.assertIsNone(data["previous"])
        self.assertEqual(data["next"], "http://testserver/api/v1/entities/projects/mock/?cursor=page|2|100")
        next_response = self.client.get(
            "/api/v1/entities/projects/mock/?cursor=page|2|100",
            headers={"content-type": "application/json"}
        )
        self.assertEqual(next_response.status_code, 200)
        next_data = next_response.json()
        self.assertEqual(next_data["count"], 200)
        next_results = next_data.pop("results")
        self.assertEqual(len(next_results), 100)
        self.assertEqual(next_data["previous"], "http://testserver/api/v1/entities/projects/mock/?cursor=page|1|100")
        self.assertIsNone(next_data["next"])
