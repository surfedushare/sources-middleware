from datetime import datetime, timedelta

from django.utils.timezone import now

from sources.tests.extraction.base import ExtractorTestCase


class TestProjectsExtraction(ExtractorTestCase):

    source = "hanze"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 302)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_status(self):
        self.assertEqual(self.results[0]["status"], "finished")
        self.assertEqual(self.results[4]["status"], "unknown")

    def test_raw_get_status(self):
        today = now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        def build_test_node(start: datetime | None, end: datetime | None):
            return {
                "period": {
                    "startDate": start.strftime("%Y-%m-%d") if start else None,
                    "endDate": end.strftime("%Y-%m-%d") if end else None,
                }
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
        self.assertEqual(self.results[0]["title"], "Ontwerpend onderzoek, coproductie in context van krimp\t")
        self.assertEqual(
            self.results[1]["title"],
            "Ph.D -project 'The Impact of the Hospital Environment: "
            "Understanding the Experience of the Patient Journey'",
            "Expected English title when Dutch title is missing"
        )
        self.assertEqual(
            self.results[2]["title"], "Water Co-Governance for Sustainable Ecosystems (Nederlands)",
            "Expected Dutch title to get preference over English title"
        )

    def test_get_description(self):
        self.assertTrue(
            self.results[0]["description"].startswith("ontwerpend onderzoek"),
            "Expected description to start with keyfindings when layman description is missing"
        )
        self.assertIn(
            "</br></br>Het project ‘Ontwerpend onderzoek", self.results[0]["description"],
            "Expected description to contain project description when keyfindings are present"
        )
        self.assertTrue(
            self.results[1]["description"].startswith("Patients very fear. Much sad."),
            "Expected description to start with project description when layman description and keyfindings are missing"
        )
        self.assertNotIn(
            "</br></br>", self.results[1]["description"],
            "Expected description to contain no newlines if only a project description is available"
        )
        self.assertIsNone(
            self.results[6]["description"],
            "Expected description to be None when no descriptions are present"
        )
        self.assertEqual(
            self.results[2]["description"], "De natuurlijke omgeving is afhankelijk van water",
            "Expected Dutch description to get preference over English"
        )

    def test_get_keywords(self):
        self.assertEqual(self.results[0]["keywords"], [])
        self.assertEqual(self.results[5]["keywords"], [
            "Healthy Ageing",
            "Health Enhancing Physical Activity",
            "Erasmus+",
            "Sport",
            "Physical Education",
            "Sport Coaching"
        ])

    def test_get_products(self):
        self.assertEqual(self.results[0]["products"], [])
        self.assertEqual(self.results[5]["products"], [
            "704dd447-825f-4708-ade5-212641c7428e",
            "ad23a0ac-4a65-4d6c-a46c-68c765fe5823",
            "a6924598-36a4-48df-8b2c-19ef8b7b2b9c",
            "c73279ff-e1fd-4d38-9808-64535392f4e7",
            "f6755774-34d3-494c-aa7d-536c9a1114b3",
            "e863e9ae-686b-43c3-91c5-94df33ab05ec",
            "de08013c-ae15-4283-bbf7-ca6d37e7e492",
            "8a71de9b-c1c1-4fcd-ba2e-652958bd1e0b"
        ])

    def test_get_persons(self):
        self.assertEqual(self.results[0]["persons"], [
            {"name": "Gerdy Gert Gert", "email": None, "external_id": "03157991-9fbc-4236-99d7-8c32af66f509"},
            {"name": "Kat Pax", "email": None, "external_id": "hanze:person:b7431e1498e44deb3fb129369b08d416e23f7c3b"},
        ])
        self.assertEqual(self.results[5]["persons"], [
            {"external_id": "e2d51cab-3b25-4890-b68f-10efeb49a9e9", "email": None, "name": "Johan de Acteur"}
        ])

    def test_get_owners(self):
        self.assertEqual(self.results[5]["owners"], [
            {
                "external_id": "e2d51cab-3b25-4890-b68f-10efeb49a9e9",
                "email": None,
                "name": "Johan de Acteur"
            }
        ])

    def test_research_theme(self):
        self.assertEqual(self.results[0]["research_themes"], [])
        self.assertEqual(self.results[1]["research_themes"], ["gezondheid"])


class TestPersonsExtraction(ExtractorTestCase):

    source = "hanze"
    entity = "persons"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 455)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|10|10")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_name(self):
        self.assertEqual(self.results[0]["name"], "Obi-Wan Kenobi")

    def test_get_description(self):
        self.assertEqual(self.results[0]["description"], "Personal profile", "Plain strings should be the description")
        self.assertTrue(
            self.results[1]["description"].endswith("\nMaster of Science"),
            "Expected academic qualifications to be added at end of description as list with single newlines"
        )
        self.assertIsNone(self.results[2]["description"], "Expected None if there is no description data")
        self.assertIn(
            "innovative music practices\n\n", self.results[9]["description"],
            "Expected multiple sections to be joined by two newlines"
        )
        self.assertEqual(
            len(self.results[9]["description"]), 10075,
            "Expected description concatenations to be long potentially"
        )
        expected_description_fragments = [
            "Musicians' biographical learning processes, lifelong and lifewide learning",
            "Biographical research into professional musicians, ethnographic research into innovative music practices"
        ]
        for description_fragment in expected_description_fragments:
            self.assertIn(
                description_fragment, self.results[9]["description"],
                "Expected descriptions with the same type to be joined together in final descrption"
            )

    def test_get_isni(self):
        self.assertIsNone(
            self.results[0]["isni"],
            "Isni data is not available in the data."
        )

    def test_get_is_employed(self):
        self.assertTrue(self.results[0]["is_employed"])
        self.assertFalse(self.results[1]["is_employed"])
        self.assertTrue(self.results[2]["is_employed"])

    def test_get_job_title(self):
        self.assertEqual(self.results[0]["job_title"], "PhD Candidate")
        self.assertIsNone(
            self.results[1]["job_title"],
            "Missing job titles in staffOrganizationAssociation objects should return None"
        )

    def test_get_photo_url(self):
        self.assertEqual(self.results[0]["photo_url"], None)
        self.assertEqual(self.results[1]["photo_url"], "https://testurl/api/.jpeg")

    def test_get_skill(self):
        self.assertEqual(self.results[0]["skills"], [])
        self.assertEqual(self.results[1]["skills"], [
            "intercultural communication",
            "Intercultural Competence Development"
        ])

    def test_phone(self):
        self.assertIsNone(self.results[0]["phone"])
        self.assertEqual(self.results[2]["phone"], "+312012345678")
