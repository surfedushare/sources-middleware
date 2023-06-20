from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from core.models import Source


class TestProxyFilesView(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Source.objects.create(name="Mock", slug="mock", proxy_files=True, entities={
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

    def test_get_file(self):
        response = self.client.get("/api/v1/files/mock/js/default.js")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)
        bytes_content = [byte for byte in response.streaming_content]
        self.assertTrue(
            bytes_content[0].decode("utf-8").startswith("$(document).ready"),
            "Expected to proxy rest_framework/js/default.js which contains jQuery for the rest_framework HTML pages"
        )

    def test_get_relative_file(self):
        response = self.client.get("/api/v1/files/mock/../accessing/private/file.pem")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ["Relative paths are not allowed when proxying files"])
