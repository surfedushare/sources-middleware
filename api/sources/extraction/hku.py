from datetime import datetime

from datagrowth.utils import reach

from sources.extraction.base import SingleResponseExtractProcessor, SinglePageAPIMixin


def value_or_none(node, key):
    """
    Sometimes an empty value is an empty object.
    This function replaces any falsy values with None.
    """
    return node.get(key, None) or None


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
    def get_orcid(cls, node):
        return node["ORCID"] or None

    @classmethod
    def get_name(cls, node):
        names = [node["first_name"], node["prefix"], node["last_name"]]
        return " ".join([name for name in names if name])

    @classmethod
    def get_skills(cls, node):
        skills = node.get("skills", {}).get("value", [])
        return skills if isinstance(skills, list) else [skills]

    @classmethod
    def get_themes(cls, node):
        themes = node.get("theme", {}).get("value", [])
        return themes if isinstance(themes, list) else [themes]


HkuPersonExtractProcessor.OBJECTIVE = {
    "external_id": HkuPersonExtractProcessor.get_external_id,
    "name": HkuPersonExtractProcessor.get_name,
    "first_name": "$.first_name",
    "last_name": "$.last_name",
    "prefix": "$.prefix",
    "initials": lambda node: None,
    "title": "$.title.value",
    "email": lambda node: value_or_none(node, "email"),
    "phone": lambda node: None,
    "skills": HkuPersonExtractProcessor.get_skills,
    "themes": HkuPersonExtractProcessor.get_themes,
    "description": lambda node: value_or_none(node, "description"),
    "parties": lambda node: [],
    "photo_url": "$.photo_url.transcoded",
    "isni": lambda node: None,
    "dai": lambda node: None,
    "orcid": HkuPersonExtractProcessor.get_orcid,
    "is_employed": lambda node: None,
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
        if not parties or isinstance(parties, dict):  # might be an empty object for some reason
            return []
        return [{"name": party["name"]} for party in parties if party["name"]]

    @classmethod
    def get_products(cls, node):
        if not node["resultids"]:  # might be an empty object for some reason
            return []
        product_ids = node["resultids"]["ID"] if isinstance(node["resultids"]["ID"], list) else \
            [node["resultids"]["ID"]]
        return [
            cls.build_product_id(product_id)
            for product_id in product_ids
        ]

    @classmethod
    def get_status(cls, node):
        status_value = "$.status.value"
        match reach(status_value, node):
            case "afgerond":
                return "finished"
            case "in uitvoering":
                return "ongoing"
            case "in voorbereiding":
                return "to be started"
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
        person = node.get(property_name, None)
        if not person:  # might be an empty object for some reason
            return []
        if isinstance(person, str):
            return [{
                "external_id": None,
                "email": None,
                "name": person
            }]
        return [
            {
                "external_id": None,
                "email": None,
                "name": name
            }
            for name in person["ul"]["li"]
        ]

    @classmethod
    def get_owners(cls, node):
        persons = HkuProjectExtractProcessor.get_persons(node)
        return [persons[0]] if len(persons) else []

    @classmethod
    def get_contacts(cls, node):
        persons = HkuProjectExtractProcessor.get_persons(node)
        return [persons[0]] if len(persons) else []

    @classmethod
    def get_persons(cls, node):
        persons = node.get("persons", {}).get("person", None)
        if persons is None:
            return []
        if isinstance(persons, dict):
            persons = [persons]
        return [
            {
                "external_id": HkuPersonExtractProcessor.build_person_id(person["person_id"]),
                "email": person.get("email", None),
                "name": f"{person['first_name']} {person['last_name']}"
            }
            for person in persons
        ]

    @classmethod
    def get_keywords(cls, node):
        keywords = node.get("tags").get("value", [])
        return keywords if isinstance(keywords, list) else [keywords]

    @classmethod
    def get_photo_url(cls, node):
        photo_url = node.get("header_image", None)
        photo_url = photo_url or None  # might be an empty object for some reason
        return photo_url


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
    "persons": HkuProjectExtractProcessor.get_persons,
    "keywords": HkuProjectExtractProcessor.get_keywords,
    "parties": HkuProjectExtractProcessor.get_parties,
    "products": HkuProjectExtractProcessor.get_products,
    "research_themes": lambda node: [],
    "photo_url": HkuProjectExtractProcessor.get_photo_url,
    "sia_project_reference": lambda node: None,
}
