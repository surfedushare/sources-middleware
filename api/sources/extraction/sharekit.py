from urllib.parse import urlparse, parse_qsl

from sources.extraction.base import SingleResponseExtractProcessor


class SharekitPersonExtractProcessor(SingleResponseExtractProcessor):

    @classmethod
    def get_api_count(cls, data):
        return data["meta"]["totalCount"]

    def _convert_to_cursor_link(self, input_link):
        if not input_link:
            return
        link = urlparse(input_link)
        parameters = dict(parse_qsl(link.query))
        return f"page|{parameters.get('page[number]', 1)}|{parameters['page[size]']}"

    def get_api_next_cursor(self, data):
        return self._convert_to_cursor_link(data["links"].get("next", None))

    def get_api_previous_cursor(self, data):
        return self._convert_to_cursor_link(data["links"].get("prev", None))

    @classmethod
    def get_api_results_path(cls):
        return "$.data"

    @classmethod
    def get_name(cls, node):
        attributes = node["attributes"]
        names = [attributes["firstName"], attributes["surnamePrefix"], attributes["surname"]]
        return " ".join([name.strip() for name in names if name])


SharekitPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.id",
    "name": SharekitPersonExtractProcessor.get_name,
    "first_name": "$.attributes.firstName",
    "last_name": "$.attributes.surname",
    "prefix": "$.attributes.surnamePrefix",
    "initials": "$.attributes.initials",
    "title": "$.attributes.academicTitle",
    "email": "$.attributes.email",
    "phone": lambda node: None,
    "skills": lambda node: [],
    "themes": lambda node: [],
    "description": lambda node: None,
    "parties": lambda node: [],
    "photo_url": lambda node: None,
    "isni": "$.attributes.isni",
    "dai": "$.attributes.dai",
    "orcid": "$.attributes.orcid",
    "is_employed": lambda node: None,
    "job_title": lambda node: None,
    "research_themes": lambda node: [],
}
