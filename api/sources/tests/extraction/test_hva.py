from sources.tests.extraction.base import ExtractorTestCase


class TestPersonsExtraction(ExtractorTestCase):

    source = "hva"
    entity = "persons"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 4)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|2|2")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_name(self):
        self.assertEqual(self.results[0]["name"], "Pietje Puk")
        self.assertEqual(self.results[1]["name"], "Josefien Janssen")

    def test_get_isni(self):
        self.assertIsNone(self.results[0]["isni"])
        self.assertEqual(self.results[1]["isni"], "0000000011111111")

    def test_get_is_employed(self):
        self.assertFalse(self.results[0]["is_employed"])
        self.assertTrue(self.results[1]["is_employed"])
