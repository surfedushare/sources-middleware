from urllib.parse import urlparse, parse_qsl

from django.urls import reverse

from sources.extraction.base import SingleResponseExtractProcessor


class MockAPIMixin(object):

    response = None
    config = None

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    @classmethod
    def get_api_results_path(cls):
        return "$.results"

    def _convert_to_cursor_link(self, request, input_link):
        if not input_link:
            return
        link = urlparse(input_link)
        parameters = dict(parse_qsl(link.query))
        cursor = f"page|{parameters.get('page', 1)}|{parameters['page_size']}"
        base_url = reverse("v1:entities", args=(self.config.entity, request.resolver_match.kwargs["source"]))
        return f"{request.build_absolute_uri(base_url)}?cursor={cursor}"

    def get_api_next_cursor_link(self, request, data):
        return self._convert_to_cursor_link(request, data["next"])

    def get_api_previous_cursor_link(self, request, data):
        return self._convert_to_cursor_link(request, data["previous"])


class MockPersonExtractProcessor(SingleResponseExtractProcessor, MockAPIMixin):
    pass


MockPersonExtractProcessor.OBJECTIVE = {
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
}


class MockProjectExtractProcessor(SingleResponseExtractProcessor, MockAPIMixin):
    pass


MockProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.external_id",
    "title": "$.title",
    "status": "$.status.value",
    "started_at": "$.started_at",
    "ended_at": "$.ended_at",
    "coordinates": "$.coordinates",
    "goal": "$.goal",
    "description": "$.description",
    "contact": "$.contact",
    "owner": "$.owner",
    "persons": "$.persons",
    "keywords": "$.tags.value",
    "parties": "$.parties",
    "products": "$.resultids.ID"
}
