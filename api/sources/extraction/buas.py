from datetime import datetime
from dateutil.parser import parse as date_parser

from sources.extraction.base import SingleResponseExtractProcessor
from sources.extraction.pure import PureAPIMixin


class BuasPersonExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def get_name(cls, node):
        return f"{node['name']['firstName']} {node['name']['lastName']}"

    @classmethod
    def get_is_employed(cls, node):
        today = datetime.today()
        for association in node.get("staffOrganisationAssociations", []):
            end_date = association.get("period", None).get("endDate", None)
            if not end_date or date_parser(end_date, ignoretz=True) > today:
                break
        else:
            return False
        return True


BuasPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "name": BuasPersonExtractProcessor.get_name,
    "first_name": "$.name.firstName",
    "last_name": "$.name.lastName",
    "prefix": lambda node: None,
    "initials": lambda node: None,
    "title": lambda node: None,
    "email": lambda node: None,
    "phone": lambda node: None,
    "skills": lambda node: [],
    "themes": lambda node: [],
    "description": lambda node: None,
    "parties": lambda node: [],
    "photo_url": lambda node: None,
    "isni": lambda node: None,
    "dai": lambda node: None,
    "orcid": "$.orcid",
    "is_employed": BuasPersonExtractProcessor.get_is_employed
}


class BuasProjectExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def get_parties(cls, node):
        return [
            {"name": party["externalOrganisation"]["name"]["text"][0]["value"]}
            for party in node.get("collaborators", [])
        ]

    @classmethod
    def get_products(cls, node):
        return [product["uuid"] for product in node.get("relatedResearchOutputs", [])]


BuasProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "title": "$.title.text.0.value",
    "status": "$.status.key",
    "started_at": "$.period.startDate",
    "ended_at": "$.period.endDate",
    "coordinates": lambda node: [],
    "goal": lambda node: None,
    "description": "$.descriptions.0.value.text.0.value",
    "contact": lambda node: None,
    "owner": lambda node: None,
    "persons": lambda node: [],
    "keywords": "$.keywordGroups.0.keywordContainers.0.freeKeywords.0.freeKeywords",
    "parties": BuasProjectExtractProcessor.get_parties,
    "products": BuasProjectExtractProcessor.get_products
}
