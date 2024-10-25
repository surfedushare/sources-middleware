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

    def test_get_description(self):
        self.assertIsNone(self.results[0]["description"])
        self.assertTrue(
            self.results[1]["description"].startswith(
                "<p><strong>Oscar Bastiaens</strong> (1990) is a researcher and lecturer"
            )
        )

    def test_get_skills(self):
        self.assertIsNone(self.results[0]["skills"])
        self.assertEqual(self.results[1]["skills"], [
            "Multi-narrative design (transmedia)", "semiotics", "virtual reality"
        ])

    def test_get_email(self):
        self.assertIsNone(self.results[0]["email"])
        self.assertEqual(self.results[1]["email"], "bassie@buas.nl")

    def test_get_photo_url(self):
        self.assertIsNone(self.results[0]["photo_url"])
        self.assertEqual(self.results[1]["photo_url"], "https://pure.buas.nl/ws/files/251152/Bassie_Ozzie.jpg")

    def test_get_is_employed(self):
        self.assertFalse(self.results[0]["is_employed"])
        self.assertTrue(self.results[1]["is_employed"])
        self.assertFalse(self.results[2]["is_employed"])

    def test_get_job_title(self):
        self.assertIsNone(self.results[0]["job_title"])
        self.assertEqual(self.results[1]["job_title"], "Lecturer")
        self.assertIsNone(self.results[2]["job_title"])


class TestProjectsExtraction(ExtractorTestCase):

    source = "buas"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 162)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_status(self):
        self.assertEqual(self.results[0]["status"], "finished")
        self.assertEqual(self.results[1]["status"], "preparing")
        self.assertEqual(self.results[31]["status"], "ongoing")

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
        self.assertEqual(self.results[0]["persons"], [
            {"external_id": "4f3e10ea-c09b-4f9e-98bb-7407d1340112", "email": None, "name": "Ikke Vogelaar"},
            {"external_id": "97ee5bd3-2145-4a4a-9a61-827e2ec839ef", "email": None, "name": "Pietje Peter"},
            {"name": "Kat Pax", "email": None, "external_id": "buas:person:b7431e1498e44deb3fb129369b08d416e23f7c3b"},
        ])

    def test_get_owners(self):
        self.assertEqual(self.results[0]["owners"], [
            {
                "external_id": "4f3e10ea-c09b-4f9e-98bb-7407d1340112",
                "email": None,
                "name": "Ikke Vogelaar"
            }
        ])
