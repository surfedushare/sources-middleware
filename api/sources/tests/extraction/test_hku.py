from sources.tests.extraction.base import ExtractorTestCase


class TestPersonsExtraction(ExtractorTestCase):

    source = "hku"
    entity = "persons"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 1)

    def test_get_external_id(self):
        self.assertEqual(self.results[0]["external_id"], "hku:person:1")

    def test_get_name(self):
        self.assertEqual(self.results[0]["name"], "Pietje Puk")

    def test_get_skills(self):
        self.assertEqual(self.results[0]["skills"], [])

    def test_get_themes(self):
        self.assertEqual(self.results[0]["themes"], ["Taal, Cultuur en Kunsten", "Techniek"])


class TestProjectsExtraction(ExtractorTestCase):

    source = "hku"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 2)

    def test_get_external_id(self):
        self.assertEqual(self.results[0]["external_id"], "hku:project:1")

    def test_get_status(self):
        self.assertEqual(self.results[0]["status"], "ongoing")
        self.assertEqual(self.results[1]["status"], "finished")

    def test_get_coordinates(self):
        self.assertEqual(self.results[0]["coordinates"], ["52.0958071", "5.1115789"])

    def test_get_skills(self):
        self.assertEqual(self.results[0]["parties"], [{"name": "SURF"}])

    def test_get_products(self):
        self.assertEqual(self.results[0]["products"], ["hku:product:1", "hku:product:2"])

    def test_lambda_owner(self):
        self.assertEqual(self.results[0]["owner"], "Pietje Puk")
        self.assertIsNone(self.results[1]["owner"])

    def test_lambda_contact(self):
        self.assertEqual(self.results[0]["contact"], "Pietje Puk")
        self.assertEqual(self.results[1]["contact"], "Falkon Hub Hub")
