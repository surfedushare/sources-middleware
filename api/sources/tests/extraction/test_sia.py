from sources.tests.extraction.base import ExtractorTestCase


class TestProjectsExtraction(ExtractorTestCase):
    """
    NB: This test case uses a data product that comes from the SourceIdentifierListProxy class.
    This data product is stored in the fixtures/sia/projects.json file, but this is not an actual response from an API.
    Instead it is a data product created from multiple API responses by the SourceIdentifierListProxy.
    """

    source = "sia"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 100)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))
