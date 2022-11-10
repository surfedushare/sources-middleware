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
        self.assertEqual(self.extractor.get_api_count(self.extractor.data), 200)

    def test_get_api_next_cursor(self):
        self.assertEqual(self.extractor.get_api_next_cursor(self.extractor.data), "offset|100|100")

    def test_get_api_previous_cursor(self):
        self.assertIsNone(self.extractor.get_api_previous_cursor(self.extractor.data))

    def test_get_parties(self):
        self.assertEqual(
            self.results[0]["parties"],
            [
                {"name": "Hogeschool van Amsterdam"},
                {"name": "College van Clubartsen en Consulenten (CCC)"},
                {"name": "Koninklijke Nederlandse Voetbalbond (KNVB)"},
                {"name": "N.V.F.S."},
                {"name": "Stichting Nederlands Paramedisch Instituut (NPI)"},
                {"name": "TNO Kwaliteit van Leven"},
                {"name": "Vereniging Fysiotherapeuten binnen het Betaald Voetbal (VFBV)"},
                {"name": "Vereniging voor Sportgeneeskunde (VSG)"},
                {"name": "ADO Den Haag"},
                {"name": "AZ"},
                {"name": "BVO Sparta Rotterdam"},
                {"name": "De Sportartsen Groep"},
                {"name": "FC Dordrecht"},
                {"name": "FC Groningen Fysiotherapie"},
                {"name": "FC Utrecht"},
                {"name": "Fysiotherapie Dukenburg"},
                {"name": "Fysiotherapie Utrecht Oost"},
                {"name": "NEC Nijmegen"},
                {"name": "Paramedisch Centrum Simpelveld"},
                {"name": "SC Heerenveen BVO"},
                {"name": "SportmedX"},
                {"name": "Stichting Betaald Voetbal Excelsior"},
                {"name": "Willem II"}
            ]
        )
