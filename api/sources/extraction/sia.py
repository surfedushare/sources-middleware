from django.conf import settings
from sources.extraction.base import SingleResponseExtractProcessor


class SiaProjectExtractProcessor(SingleResponseExtractProcessor):

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    @classmethod
    def get_api_results_path(cls):
        return "$.results"

    def get_api_next_cursor(self, data):
        info = data["pagination"]
        next_offset = info['offset'] + info['size']
        if next_offset > self.get_api_count(data):
            return
        return f"offset|{next_offset}|{info['size']}"

    def get_api_previous_cursor(self, data):
        info = data["pagination"]
        previous_offset = info['offset'] - info['size']
        if previous_offset < 0:
            return
        return f"offset|{previous_offset}|{info['size']}"

    @classmethod
    def get_status(cls, node):
        match node["status"]:
            case "Afgerond":
                return "finished"
            case _:
                return "unknown"

    @classmethod
    def get_parties(cls, node):
        contact_parties = [{"name": node["contactinformatie"]["naam"]}]
        network_parties = [{"name": network_party["naam"]} for network_party in node["netwerkleden"]]
        consortium_parties = [{"name": network_party["naam"]} for network_party in node["consortiumpartners"]]
        return contact_parties + consortium_parties + network_parties


SiaProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.id",
    "title": "$.titel",
    "status": SiaProjectExtractProcessor.get_status,
    "started_at": "$.startdatum",
    "ended_at": "$.einddatum",
    "coordinates": lambda node: [],
    "goal": "$.eindrapportage",
    "description": "$.samenvatting",
    "contact": lambda node: settings.SIA_CONTACT_EMAIL,  # takes value from an AWS secret, will be None on localhost
    "owner": lambda node: settings.SIA_CONTACT_EMAIL,  # takes value from an AWS secret, will be None on localhost
    "persons": lambda node: [],
    "keywords": lambda node: None,
    "parties": SiaProjectExtractProcessor.get_parties,
    "products": lambda node: [],
}
