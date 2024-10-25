from datetime import datetime
from dateutil.parser import parse as parse_date

from sources.extraction.base import SingleResponseExtractProcessor, SinglePageAPIMixin


class HUPersonExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):
    pass


HUPersonExtractProcessor.OBJECTIVE = {
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
    "themes": "$.themes",
    "description": "$.description",
    "parties": "$.parties",
    "isni": "$.isni",
    "dai": "$.dai",
    "orcid": "$.orcid",
    "is_employed": "$.is_employed",
    "job_title": "$.job_title",
    "research_themes": "$.research_themes",
    "photo_url": "$.photo_url",
}


class HUProjectExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

    @classmethod
    def get_status(cls, node):
        today = datetime.today()
        ended_at = parse_date(node["ended_at"]) if node.get("ended_at") else None
        started_at = parse_date(node["started_at"]) if node.get("started_at") else None
        if started_at and started_at > today:
            return "preparing"
        elif ended_at and ended_at > today or not ended_at and started_at:
            return "ongoing"
        elif ended_at and ended_at <= today:
            return "finished"
        else:
            return "unknown"


HUProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.external_id",
    "title": "$.title",
    "status": HUProjectExtractProcessor.get_status,
    "started_at": "$.started_at",
    "ended_at": "$.ended_at",
    "coordinates": "$.coordinates",
    "goal": "$.goal",
    "description": "$.description",
    "contacts": "$.contacts",
    "owners": "$.contacts",
    "persons": "$.persons",
    "keywords": "$.keywords",
    "parties": "$.parties",
    "products": "$.products",
    "research_themes": "$.research_themes",
    "photo_url": "$.photo_url",
}
