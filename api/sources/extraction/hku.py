from sources.extraction.base import SingleResponseExtractProcessor, SinglePageAPIMixin


class HkuPersonExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

    @classmethod
    def get_api_count(cls, data):
        return len(data["root"]["item"])

    @classmethod
    def get_api_results_path(cls):
        return "$.root.item"

    @classmethod
    def get_name(cls, node):
        names = [node["first_name"], node["prefix"], node["last_name"]]
        return " ".join([name for name in names if name])

    @classmethod
    def get_skills(cls, node):
        return node.get("skills").get("value", [])

    @classmethod
    def get_theme(cls, node):
        return node.get("theme").get("value", [])


HkuPersonExtractProcessor.OBJECTIVE = {
    "external_id": "$.personid",
    "name": HkuPersonExtractProcessor.get_name,
    "first_name": "$.first_name",
    "last_name": "$.last_name",
    "prefix": "$.prefix",
    "initials": lambda node: None,
    "title": "$.title.value",
    "email": "$.email",
    "phone": lambda node: None,
    "skills": HkuPersonExtractProcessor.get_skills,
    "theme": HkuPersonExtractProcessor.get_theme,
    "description": "$.description",
    "parties": lambda node: [],
    "photo_url": "$.photo_url.transcoded",
    "isni": lambda node: None,
    "dai": lambda node: None,
    "orcid": lambda node: None,
}


class HkuProjectExtractProcessor(SingleResponseExtractProcessor, SinglePageAPIMixin):

    @classmethod
    def get_api_count(cls, data):
        return len(data["root"]["project"])

    @classmethod
    def get_api_results_path(cls):
        return "$.root.project"

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
        pass


HkuProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.projectid",
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
    "products": "$.resultids.ID"
}
