from sources.tests.extraction.base import ExtractorTestCase


class TestPersonsExtraction(ExtractorTestCase):

    source = "hu"
    entity = "persons"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 513)

    def test_get_external_id(self):
        self.assertEqual(self.results[0]["external_id"], "4bc16849-1e9a-4b37-8c66-860ce2f01c69")

    def test_get_name(self):
        self.assertEqual(self.results[0]["name"], "Aap van der Mies")

    def test_get_first_name(self):
        self.assertEqual(self.results[0]["first_name"], "Aap")

    def test_get_last_name(self):
        self.assertEqual(self.results[0]["last_name"], "van der Mies")

    def test_get_description(self):
        self.assertEqual(self.results[0]["description"], "<p>Hij is een baas</p>")

    def test_get_orcid(self):
        self.assertEqual(self.results[0]["orcid"], "0000-0000-0000-0000")

    def test_get_job_title(self):
        self.assertEqual(self.results[0]["job_title"], "Onderzoeker")


class TestProjectsExtraction(ExtractorTestCase):

    source = "hu"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 368)

    def test_get_external_id(self):
        self.assertEqual(self.results[0]["external_id"], "1cd33732-7513-4004-9486-aa2d8f38215f")

    def test_get_status(self):
        self.assertEqual(self.results[0]["status"], "finished")
        self.assertEqual(self.results[1]["status"], "ongoing")
        self.assertEqual(self.results[2]["status"], "unknown")

    def test_get_title(self):
        self.assertEqual(self.results[0]["title"], "360 graden newsroom")

    def test_get_started_at(self):
        self.assertEqual(self.results[0]["started_at"], "2022-10-01")

    def test_get_ended_at(self):
        self.assertEqual(self.results[0]["ended_at"], "2020-12-22")
