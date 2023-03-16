import os
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
        # Gather all possible descriptions
        language_code = None
        descriptions = {}
        for description in node["descriptions"]:
            if "value" not in description:
                continue
            if language_code is None:
                language_code = list(description["value"].keys())[0]
            description_type = os.path.split(description["type"]["uri"])[1]
            descriptions[description_type] = description["value"][language_code]
        # Concatenate different descriptions to be a singular text
        description = ""
        if "laymansdescription" in descriptions:
            description += descriptions["laymansdescription"]

        if "keyfindings" in descriptions:
            if description:
                description += "</br></br>"
            description += descriptions["keyfindings"]
        if "projectdescription" in descriptions:
            if description:
                description += "</br></br>"
            description += descriptions["projectdescription"]
        return description or None

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
        persons = []
        for participant in node.get("participants", []):
            if "person" in participant:
                person = participant["person"]
            elif "externalPerson" in participant:
                person = participant["externalPerson"]
            else:
                continue
            persons.append({
                "external_id": person["uuid"],
                "email": None,
                "name": f"{participant['name']['firstName']} {participant['name']['lastName']}"
            })
        return persons

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
