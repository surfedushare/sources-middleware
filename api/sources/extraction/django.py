from urllib.parse import urlparse, parse_qsl

from sources.extraction.base import SingleResponseExtractProcessor


class DjangoAPIMixin(object):

    response = None
    config = None

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    @classmethod
    def get_api_results_path(cls):
        return "$.results"

    def _convert_to_cursor_link(self, input_link):
        if not input_link:
            return
        link = urlparse(input_link)
        parameters = dict(parse_qsl(link.query))
        return f"page|{parameters.get('page', 1)}|{parameters['page_size']}"

    def get_api_next_cursor(self, data):
        return self._convert_to_cursor_link(data["next"])

    def get_api_previous_cursor(self, data):
        return self._convert_to_cursor_link(data["previous"])


class DjangoPersonExtractProcessor(SingleResponseExtractProcessor, DjangoAPIMixin):
    pass


DjangoPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.external_id",
    "name": "$.name",
    "first_name": "$.first_name",
    "last_name": "$.last_name",
    "prefix": "$.prefix",
    "initials": "$.initials",
    "title": "$.title",
    "email": "$.email",
    "phone": "$.phone",
    "skills": "$.skills",
    "theme": "$.theme",
    "description": "$.description",
    "parties": "$.parties",
    "photo_url": "$.photo_url",
    "isni": "$.isni",
    "dai": "$.dai",
    "orcid": "$.orcid",
    "is_employed": "$.is_employed",
    "job_title": "$.job_title",
}


class DjangoProjectExtractProcessor(SingleResponseExtractProcessor, DjangoAPIMixin):
    pass


DjangoProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.external_id",
    "title": "$.title",
    "status": "$.status.value",
    "started_at": "$.started_at",
    "ended_at": "$.ended_at",
    "coordinates": "$.coordinates",
    "goal": "$.goal",
    "description": "$.description",
    "contacts": "$.contacts",
    "owners": "$.owners",
    "persons": "$.persons",
    "keywords": "$.tags.value",
    "parties": "$.parties",
    "products": "$.resultids.ID",
    "research_themes": "$.research_themes",
}
