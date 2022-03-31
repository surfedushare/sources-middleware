from sources.extraction.base import SingleResponseExtractProcessor


class MockAPIMixin(object):

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    @classmethod
    def get_api_results_path(cls):
        return "$.results"

    @classmethod
    def get_api_next_cursor(cls, data):
        return data["next"]

    @classmethod
    def get_api_previous_cursor(cls, data):
        return data["previous"]


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
