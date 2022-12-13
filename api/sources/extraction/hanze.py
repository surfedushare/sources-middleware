from datetime import datetime
from dateutil.parser import parse as date_parser

from sources.extraction.base import SingleResponseExtractProcessor
from sources.extraction.pure import PureAPIMixin


class HanzeProjectExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def get_status(cls, node):
        today = datetime.today()
        end_date = node.get("period", {}).get("endDate")
        return "ongoing" if not end_date or today <= date_parser(end_date) else "finished"

    @classmethod
    def get_title(cls, node):
        title = node["title"]
        return list(title.values())[0]

    @classmethod
    def get_description(cls, node):
        descriptions = [description for description in node["descriptions"] if "value" in description]
        if not descriptions:
            return
        description = descriptions[0]
        return list(description["value"].values())[0]

    @classmethod
    def get_keywords(cls, node):
        keyword_groups = [
            keyword_group for keyword_group in node.get("keywordGroups", [])
            if keyword_group.get("logicalName", None) == "keywordContainers"
        ]
        if not keyword_groups:
            return []
        keywords = []
        for keyword_group in keyword_groups:
            keywords += keyword_group["keywords"][0]["freeKeywords"]
        return keywords

    @classmethod
    def get_products(cls, node):
        return [product["researchOutput"]["uuid"] for product in node.get("researchOutputs", [])]

    @classmethod
    def get_persons(cls, node):
        person_ids = []
        for participant in node.get("participants", []):
            if "person" in participant:
                person = participant["person"]
            elif "externalPerson" in participant:
                person = participant["externalPerson"]
            else:
                continue
            person_ids.append(person["uuid"])
        return person_ids

    @classmethod
    def get_owner(cls, node):
        persons = cls.get_persons(node)
        if persons:
            return persons[0]


HanzeProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "title": HanzeProjectExtractProcessor.get_title,
    "status": HanzeProjectExtractProcessor.get_status,
    "started_at": "$.period.startDate",
    "ended_at": "$.period.endDate",
    "coordinates": lambda node: [],
    "goal": lambda node: None,
    "description": HanzeProjectExtractProcessor.get_description,
    "contact": HanzeProjectExtractProcessor.get_owner,
    "owner": HanzeProjectExtractProcessor.get_owner,
    "persons": HanzeProjectExtractProcessor.get_persons,
    "keywords": HanzeProjectExtractProcessor.get_keywords,
    "parties": lambda node: [],
    "products": HanzeProjectExtractProcessor.get_products
}
