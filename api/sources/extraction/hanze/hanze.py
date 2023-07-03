import os
from datetime import datetime
from dateutil.parser import parse as date_parser

from sources.extraction.base import SingleResponseExtractProcessor
from sources.extraction.hanze.research_themes import ASJC_TO_RESEARCH_THEME
from sources.extraction.pure import PureAPIMixin


class HanzePersonsExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):
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
        for association in node.get("staffOrganizationAssociations", []):
            end_date = association["period"].get("endDate", None)
            if not end_date or date_parser(end_date) > today:
                break
        else:
            return False
        return True

    @classmethod
    def get_photo_url(cls, node):
        photo_list = node.get("profilePhotos", None)
        if not photo_list:
            return
        photo_url = photo_list[0].get("url", None)
        if not photo_url:
            return
        return photo_list[0]["url"]

    @classmethod
    def get_job_title(cls, node):
        today = datetime.today()
        for association in node.get("staffOrganizationAssociations", []):
            end_date = association.get("period", None).get("endDate", None)
            if not end_date or date_parser(end_date, ignoretz=True) > today:
                break
        else:
            return
        job_title_object = association.get("jobTitle", None)
        if not job_title_object:
            return
        return next(iter(job_title_object["term"].values()), None)


HanzePersonsExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "name": HanzePersonsExtractProcessor.get_name,
    "first_name": "$.name.firstName",
    "last_name": "$.name.lastName",
    "prefix": lambda node: None,
    "initials": lambda node: None,
    "title": lambda node: None,
    "email": "$.user.email",
    "phone": lambda node: None,
    "skills": lambda node: [],
    "themes": lambda node: [],
    "description": lambda node: None,
    "parties": lambda node: [],
    "photo_url": HanzePersonsExtractProcessor.get_photo_url,
    "isni": HanzePersonsExtractProcessor.get_isni,
    "dai": lambda node: None,
    "orcid": "$.orcid",
    "is_employed": HanzePersonsExtractProcessor.get_is_employed,
    "job_title": HanzePersonsExtractProcessor.get_job_title,
    "research_themes": lambda node: [],
}


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
            description_text = description["value"].get(language_code, None)
            if description_text:
                descriptions[description_type] = description_text
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
    def get_owners(cls, node):
        persons = cls.get_persons(node)
        return [persons[0]] if persons else []

    @classmethod
    def get_research_themes(cls, node):
        research_themes = []
        for keywords in node.get("keywordGroups", []):
            if keywords["logicalName"] == "ASJCSubjectAreas":
                asjc_identifiers = [
                    classification["uri"].replace("/dk/atira/pure/subjectarea/asjc/", "")
                    for classification in keywords["classifications"]
                ]
                research_themes += [ASJC_TO_RESEARCH_THEME[identifier] for identifier in asjc_identifiers]
        return research_themes


HanzeProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "title": HanzeProjectExtractProcessor.get_title,
    "status": HanzeProjectExtractProcessor.get_status,
    "started_at": "$.period.startDate",
    "ended_at": "$.period.endDate",
    "coordinates": lambda node: [],
    "goal": lambda node: None,
    "description": HanzeProjectExtractProcessor.get_description,
    "contacts": HanzeProjectExtractProcessor.get_owners,
    "owners": HanzeProjectExtractProcessor.get_owners,
    "persons": HanzeProjectExtractProcessor.get_persons,
    "keywords": HanzeProjectExtractProcessor.get_keywords,
    "parties": lambda node: [],
    "products": HanzeProjectExtractProcessor.get_products,
    "research_themes": HanzeProjectExtractProcessor.get_research_themes,
}
