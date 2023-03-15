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

    def test_get_isni(self):
        self.assertIsNone(
            self.results[0]["isni"],
            "According to Jasper Bedaux in an email on 15th Feb 2023 Hva won't pass along ISNI."
        )

    def test_get_is_employed(self):
        self.skipTest(
            "According to Jasper Bedaux in an email on 6th March 2023 HvA won't pass along non-employed people"
        )

    def test_get_job_title(self):
        self.assertEqual(self.results[0]["job_title"], "Senior Lecturer")
        self.assertIsNone(
            self.results[1]["job_title"],
            "Missing job titles in staffOrganizationAssociation objects should return None"
        )
