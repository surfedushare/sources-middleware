import os
from datetime import datetime
from dateutil.parser import parse as date_parser
from hashlib import sha1

from django.utils.html import strip_tags

from sources.extraction.base import SingleResponseExtractProcessor
from sources.extraction.pure import PureAPIMixin


class BuasPersonExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def parse_profile_information(cls, node, info_type):
        for profile_information in node.get("profileInformations", []):
            profile_information_uri = profile_information.get("type").get("uri")
            _, profile_information_type = os.path.split(profile_information_uri)
            if profile_information_type == info_type:
                return profile_information.get("value").get("text")[0].get("value")

    @classmethod
    def parse_current_staff_association(cls, node):
        today = datetime.today()
        for association in node.get("staffOrganisationAssociations", []):
            end_date = association.get("period", None).get("endDate", None)
            if not end_date or date_parser(end_date, ignoretz=True) > today:
                return association

    @classmethod
    def get_name(cls, node):
        return f"{node['name']['firstName']} {node['name']['lastName']}"

    @classmethod
    def get_description(cls, node):
        return cls.parse_profile_information(node, "researchinterests")

    @classmethod
    def get_skills(cls, node):
        raw_skills = cls.parse_profile_information(node, "subjects")
        if not raw_skills:
            return
        skills = strip_tags(raw_skills).split(",")
        return [skill.strip() for skill in skills]

    @classmethod
    def get_email(cls, node):
        staff_association = cls.parse_current_staff_association(node)
        if not staff_association:
            return
        for email in staff_association.get("emails", []):
            return email.get("value").get("value")

    @classmethod
    def get_is_employed(cls, node):
        staff_association = cls.parse_current_staff_association(node)
        return bool(staff_association)

    @classmethod
    def get_photo_url(cls, node):
        profile_photos = node.get("profilePhotos", [])
        if not profile_photos:
            return
        return profile_photos[0]["url"]

    @classmethod
    def get_job_title(cls, node):
        today = datetime.today()
        for association in node.get("staffOrganisationAssociations", []):
            end_date = association.get("period", None).get("endDate", None)
            if not end_date or date_parser(end_date, ignoretz=True) > today:
                break
        else:
            return
        job_title_object = association.get("jobTitle", association.get("jobDescription", None))
        if not job_title_object:
            return
        elif "term" in job_title_object:
            job_title_object = job_title_object["term"]
        return job_title_object["text"][0]["value"]


BuasPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "name": BuasPersonExtractProcessor.get_name,
    "first_name": "$.name.firstName",
    "last_name": "$.name.lastName",
    "prefix": lambda node: None,
    "initials": lambda node: None,
    "title": lambda node: None,
    "email": BuasPersonExtractProcessor.get_email,
    "phone": lambda node: None,
    "skills": BuasPersonExtractProcessor.get_skills,
    "themes": lambda node: [],
    "description": BuasPersonExtractProcessor.get_description,
    "parties": lambda node: [],
    "photo_url": BuasPersonExtractProcessor.get_photo_url,
    "isni": lambda node: None,
    "dai": lambda node: None,
    "orcid": "$.orcid",
    "is_employed": BuasPersonExtractProcessor.get_is_employed,
    "job_title": BuasPersonExtractProcessor.get_job_title,
    "research_themes": lambda node: [],
}


class BuasProjectExtractProcessor(SingleResponseExtractProcessor, PureAPIMixin):

    @classmethod
    def get_status(cls, node):
        match node["status"]["key"]:
            case "FINISHED":
                return "finished"
            case "RUNNING":
                return "ongoing"
            case "NOT_STARTED":
                return "to be started"
            case _:
                return "unknown"

    @classmethod
    def get_parties(cls, node):
        return [
            {"name": party["externalOrganisation"]["name"]["text"][0]["value"]}
            for party in node.get("collaborators", [])
        ]

    @classmethod
    def get_products(cls, node):
        return [product["uuid"] for product in node.get("relatedResearchOutputs", [])]

    @classmethod
    def get_persons(cls, node):
        persons = []
        for participant in node.get("participants", []):
            name = participant.get('name', {})
            match name:
                case {"firstName": first_name}:
                    full_name = f"{first_name} {name['lastName']}"
                case {"lastName": last_name}:
                    full_name = last_name
                case _:
                    # Contributors with the type: ExternalContributorAssociation sometimes
                    # do not yield any name or other identity information.
                    # We skip the (useless) data silently
                    continue
            is_external = "externalPerson" in participant
            person_data = participant.get("person", {}) if not is_external else participant.get("externalPerson", {})
            persons.append({
                "name": full_name,
                "email": None,
                "external_id": person_data.get("uuid",
                                               f"buas:person:"
                                               f"{sha1(full_name.encode('utf-8')).hexdigest()}"),

            })
        return persons

    @classmethod
    def get_owners(cls, node):
        persons = cls.get_persons(node)
        return [persons[0]] if persons else []


BuasProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.uuid",
    "title": "$.title.text.0.value",
    "status": BuasProjectExtractProcessor.get_status,
    "started_at": "$.period.startDate",
    "ended_at": "$.period.endDate",
    "coordinates": lambda node: [],
    "goal": lambda node: None,
    "description": "$.descriptions.0.value.text.0.value",
    "contacts": BuasProjectExtractProcessor.get_owners,
    "owners": BuasProjectExtractProcessor.get_owners,
    "persons": BuasProjectExtractProcessor.get_persons,
    "keywords": "$.keywordGroups.0.keywordContainers.0.freeKeywords.0.freeKeywords",
    "parties": BuasProjectExtractProcessor.get_parties,
    "products": BuasProjectExtractProcessor.get_products,
    "research_themes": lambda node: [],
    "photo_url": lambda node: None,
    "sia_project_reference": None,
}
