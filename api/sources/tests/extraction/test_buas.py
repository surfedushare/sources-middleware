from sources.tests.extraction.base import ExtractorTestCase


class TestPersonsExtraction(ExtractorTestCase):

    source = "buas"
    entity = "persons"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 398)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_name(self):
        self.assertEqual(self.results[0]["name"], "F Maggie")

    def test_get_is_employed(self):
        self.assertFalse(self.results[0]["is_employed"])
        self.assertTrue(self.results[1]["is_employed"])


class TestProjectsExtraction(ExtractorTestCase):

    source = "buas"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 162)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_parties(self):
        self.assertEqual(
            self.results[0]["parties"],
            [
                {"name": "Camptoo"},
                {"name": "DEOdrive"}, 
                {"name": "Dutch Innovation Centre for Electric Road Transport (Dutch-INCERT)"}, 
                {"name": "Emodz"}, {"name": "EMOSS"}, 
                {"name": "EVConsult"},
                {"name": "Hansa Green Tour"}, 
                {"name": "Rijksdienst voor Ondernemend Nederland (RVO.nl)"}
            ]
        )

    def test_get_products(self):
        self.assertEqual(
            self.results[0]["products"],
            ["e3a6cbe7-1606-433d-8bca-7d42e08305c2", "e4f96a7c-029b-42b3-8039-c184e31c76d0"]
        )

    def test_get_persons(self):
        self.assertEqual(
            self.results[0]["persons"],
            ["4f3e10ea-c09b-4f9e-98bb-7407d1340112", "97ee5bd3-2145-4a4a-9a61-827e2ec839ef"]
        )

    def test_get_owner(self):
        self.assertEqual(self.results[0]["owner"], "4f3e10ea-c09b-4f9e-98bb-7407d1340112")
