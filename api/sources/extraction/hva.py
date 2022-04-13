from datetime import datetime
from dateutil.parser import parse as date_parser

from sources.extraction.base import SingleResponseExtractProcessor
from sources.extraction.pure import PureAPIMixin


class HvaPersonExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def get_name(cls, node):
        return f"{node['name']['firstName']} {node['name']['lastName']}"

    @classmethod
    def get_isni(cls, node):
        isni_identifier = next(
            (identifier for identifier in node.get("identifiers", [])
             if "isni" in identifier.get("type", {}).get("uri", "")),
            None
        )
        return isni_identifier["id"] if isni_identifier else None

    @classmethod
    def get_is_employed(cls, node):
        today = datetime.today()
        for association in node["staffOrganizationAssociations"]:
            end_date = association["period"].get("endDate", None)
            if not end_date or date_parser(end_date) > today:
                break
        else:
            return False
        return True


HvaPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "name": HvaPersonExtractProcessor.get_name,
    "first_name": "$.name.firstName",
    "last_name": "$.name.lastName",
    "prefix": lambda node: None,
    "initials": lambda node: None,
    "title": lambda node: None,
    "email": lambda node: None,
    "phone": lambda node: None,
    "skills": lambda node: [],
    "theme": lambda node: None,
    "description": lambda node: None,
    "parties": lambda node: [],
    "photo_url": lambda node: None,
    "isni": HvaPersonExtractProcessor.get_isni,
    "dai": lambda node: None,
    "orcid": "$.orcid",
    "is_employed": HvaPersonExtractProcessor.get_is_employed
}
