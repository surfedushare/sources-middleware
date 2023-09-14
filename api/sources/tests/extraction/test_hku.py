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
        self.assertEqual(self.results[0]["skills"], ["skills-yo"])

    def test_get_themes(self):
        self.assertEqual(self.results[0]["themes"], ["Taal, Cultuur en Kunsten", "Techniek"])


class TestProjectsExtraction(ExtractorTestCase):

    source = "hku"
    entity = "projects"

    def test_get_api_count(self):
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 10)

    def test_get_external_id(self):
        self.assertEqual(self.results[0]["external_id"], "hku:project:6376215")

    def test_get_status(self):
        self.assertEqual(self.results[0]["status"], "ongoing")
        self.assertEqual(self.results[6]["status"], "finished")

    def test_get_coordinates(self):
        self.assertEqual(self.results[0]["coordinates"], ["52.0958071", "5.1115789"])

    def test_get_parties(self):
        self.assertEqual(self.results[0]["parties"], [])
        self.assertEqual(self.results[3]["parties"], [
            {"name": "Universiteit van Amsterdam"},
            {"name": "University Utrecht"},
            {"name": "Amsterdamse Hogeschool voor de Kunsten"},
            {"name": "STICHTING HOGESCHOOL VOOR DE KUNSTEN UTRECHT"}
        ])

    def test_get_products(self):
        self.assertEqual(self.results[0]["products"], [])
        self.assertEqual(self.results[6]["products"], [
            "hku:product:5952225",
            "hku:product:5952144",
            "hku:product:5952143",
            "hku:product:5952142",
            "hku:product:5952132",
            "hku:product:5952117"
        ])

    def test_lambda_owners(self):
        self.assertEqual(self.results[0]["owners"], [
            {
                "external_id": "hku:person:6714229",
                "email": "hello.goodbye@hku.nl",
                "name": "Hello Goodbye"
            }
        ])
        self.assertEqual(self.results[5]["owners"], [
            {
                "external_id": "hku:person:6714394",
                "email": {},
                "name": "Klaartje Klaar"
            }
        ])
        self.assertEqual(self.results[6]["owners"], [])

    def test_lambda_contacts(self):
        self.assertEqual(self.results[5]["contacts"], [
            {
                "external_id": "hku:person:6714394",
                "email": {},
                "name": "Klaartje Klaar"
            }
        ])

    def test_persons(self):
        self.assertEqual(self.results[0]["persons"], [
            {
                "external_id": "hku:person:6714229",
                "email": "hello.goodbye@hku.nl",
                "name": "Hello Goodbye"
            },
            {
                "external_id": "hku:person:6698518",
                "email": "pietje-puk@hku.nl",
                "name": "Pietje Puk"
            }
        ])
        self.assertEqual(self.results[1]["persons"], [
            {
                "external_id": "hku:person:6699825",
                "email": "christian.bale@hku.nl",
                "name": "Christian Bale"
            }
        ])
