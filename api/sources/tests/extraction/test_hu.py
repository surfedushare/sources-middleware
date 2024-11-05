from datetime import datetime, timedelta

from django.utils.timezone import now

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
        self.assertEqual(self.results[2]["status"], "finished")

    def test_raw_get_status(self):
        today = now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        def build_test_node(start: datetime | None, end: datetime | None):
            return {
                "started_at": start.strftime("%Y-%m-%d") if start else None,
                "ended_at": end.strftime("%Y-%m-%d") if end else None,
            }

        # Preparing status
        preparing = build_test_node(tomorrow, tomorrow)
        self.assertEqual(self.extractor.get_status(preparing), "to be started")
        preparing_no_end = build_test_node(tomorrow, None)
        self.assertEqual(self.extractor.get_status(preparing_no_end), "to be started")
        preparing_invalid = build_test_node(tomorrow, yesterday)
        self.assertEqual(self.extractor.get_status(preparing_invalid), "to be started")

        # Ongoing status
        ongoing = build_test_node(yesterday, tomorrow)
        self.assertEqual(self.extractor.get_status(ongoing), "ongoing")
        ongoing_no_end = build_test_node(yesterday, None)
        self.assertEqual(self.extractor.get_status(ongoing_no_end), "ongoing")
        ongoing_no_start = build_test_node(None, tomorrow)
        self.assertEqual(self.extractor.get_status(ongoing_no_start), "ongoing")

        # Finished status
        finished = build_test_node(yesterday, yesterday)
        self.assertEqual(self.extractor.get_status(finished), "finished")
        finished_no_start = build_test_node(None, yesterday)
        self.assertEqual(self.extractor.get_status(finished_no_start), "finished")

        # Unknown status
        unknown = build_test_node(None, None)
        self.assertEqual(self.extractor.get_status(unknown), "unknown")

    def test_get_title(self):
        self.assertEqual(self.results[0]["title"], "360 graden newsroom")

    def test_get_started_at(self):
        self.assertEqual(self.results[0]["started_at"], "2022-10-01")

    def test_get_ended_at(self):
        self.assertEqual(self.results[0]["ended_at"], "2020-12-22")

    def test_get_photo_url(self):
        self.assertEqual(
            self.results[0]["photo_url"],
            "https://acceptatie.hu.nl/-/media/hu/afbeeldingen/onderzoek/projecten/360-graden-newsroom.ashx"
        )
        self.assertIsNone(self.results[1]["photo_url"])
