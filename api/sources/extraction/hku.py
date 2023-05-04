from datetime import datetime

from datagrowth.utils import reach

from sources.extraction.base import SingleResponseExtractProcessor, SinglePageAPIMixin


class HkuPersonExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

    @classmethod
    def get_api_count(cls, data):
        return len(data["root"]["item"])

    @classmethod
    def get_api_results_path(cls):
        return "$.root.item"

    @classmethod
    def build_person_id(cls, identifier):
        if not identifier:
            return identifier
        return f"hku:person:{identifier}"

    @classmethod
    def get_external_id(cls, node):
        identifier = node["personid"] or None
        return cls.build_person_id(identifier)

    @classmethod
    def get_name(cls, node):
        names = [node["first_name"], node["prefix"], node["last_name"]]
        return " ".join([name for name in names if name])

    @classmethod
    def get_skills(cls, node):
        return node.get("skills").get("value", [])

    @classmethod
    def get_themes(cls, node):
        return node.get("theme").get("value", [])


HkuPersonExtractProcessor.OBJECTIVE = {
    "external_id": HkuPersonExtractProcessor.get_external_id,
    "name": HkuPersonExtractProcessor.get_name,
    "first_name": "$.first_name",
    "last_name": "$.last_name",
    "prefix": "$.prefix",
    "initials": lambda node: None,
    "title": "$.title.value",
    "email": "$.email",
    "phone": lambda node: None,
    "skills": HkuPersonExtractProcessor.get_skills,
    "themes": HkuPersonExtractProcessor.get_themes,
    "description": "$.description",
    "parties": lambda node: [],
    "photo_url": "$.photo_url.transcoded",
    "isni": lambda node: None,
    "dai": lambda node: None,
    "orcid": lambda node: None,
    "is_employed": lambda node: True,
    "job_title": lambda node: None,
    "research_themes": lambda node: [],
}


class HkuProjectExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

    @classmethod
    def parse_date(cls, date_input):
        if not date_input:
            return
        date = datetime.strptime(date_input, "%d-%M-%Y")
        return date.isoformat()

    @classmethod
    def get_api_count(cls, data):
        return len(data["root"]["project"])

    @classmethod
    def get_api_results_path(cls):
        return "$.root.project"

    @classmethod
    def build_product_id(cls, identifier):
        if not identifier:
            return identifier
        return f"hku:product:{identifier}"

    @classmethod
    def build_project_id(cls, identifier):
        if not identifier:
            return identifier
        return f"hku:project:{identifier}"

    @classmethod
    def get_external_id(cls, node):
        identifier = node["projectid"] or None
        return cls.build_project_id(identifier)

    @classmethod
    def get_coordinates(cls, node):
        coordinates = node["coordinates"].replace("lat: ", "").replace("lon: ", "").split(",")
        return coordinates

    @classmethod
    def get_parties(cls, node):
        parties = node["organisations"].get("party", [])
        if not parties:  # might be an empty object for some reason
            return []
        return [{"name": party["name"]} for party in parties]

    @classmethod
    def get_products(cls, node):
        return [
            cls.build_product_id(product_id)
            for product_id in node["resultids"]["ID"]
        ]

    @classmethod
    def get_status(cls, node):
        status_value = "$.status.value"
        match reach(status_value, node):
            case "afgerond":
                return "finished"
            case "in uitvoering":
                return "ongoing"
            case _:
                return "unknown"

    @classmethod
    def get_started_at(cls, node):
        return cls.parse_date(node["started_at"])

    @classmethod
    def get_ended_at(cls, node):
        return cls.parse_date(node["ended_at"])

    @staticmethod
    def parse_person_property(node, property_name):
        full_name = node.get(property_name, None)
        if not full_name:  # might be an empty object for some reason
            return None
        return {
            "external_id": None,
            "email": None,
            "name": full_name
        }

    @classmethod
    def get_owners(cls, node):
        owner = HkuProjectExtractProcessor.parse_person_property(node, "owner")
        if not owner:
            return []
        return [owner]

    @classmethod
    def get_contacts(cls, node):
        contact = HkuProjectExtractProcessor.parse_person_property(node, "contact")
        if not contact:
            return []
        return [contact]


HkuProjectExtractProcessor.OBJECTIVE = {
    "external_id": HkuProjectExtractProcessor.get_external_id,
    "title": "$.title",
    "status": HkuProjectExtractProcessor.get_status,
    "started_at": HkuProjectExtractProcessor.get_started_at,
    "ended_at": HkuProjectExtractProcessor.get_ended_at,
    "coordinates": HkuProjectExtractProcessor.get_coordinates,
    "goal": "$.goal",
    "description": "$.description",
    "contacts": HkuProjectExtractProcessor.get_contacts,
    "owners": HkuProjectExtractProcessor.get_owners,
    "persons": lambda node: [],
    "keywords": "$.tags.value",
    "parties": HkuProjectExtractProcessor.get_parties,
    "products": HkuProjectExtractProcessor.get_products,
    "research_themes": lambda node: [],
}
