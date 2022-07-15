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
    "is_employed": lambda node: True
}


class HkuProjectExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

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
        return [{"name": party["name"]} for party in parties]

    @classmethod
    def get_products(cls, node):
        return [
            cls.build_product_id(product_id)
            for product_id in node["resultids"]["ID"]
        ]


HkuProjectExtractProcessor.OBJECTIVE = {
    "external_id": HkuProjectExtractProcessor.get_external_id,
    "title": "$.title",
    "status": "$.status.value",
    "started_at": "$.started_at",
    "ended_at": "$.ended_at",
    "coordinates": HkuProjectExtractProcessor.get_coordinates,
    "goal": "$.goal",
    "description": "$.description",
    "contact": "$.contact",
    "owner": "$.owner",
    "persons": lambda node: [],
    "keywords": "$.tags.value",
    "parties": HkuProjectExtractProcessor.get_parties,
    "products": HkuProjectExtractProcessor.get_products
}
