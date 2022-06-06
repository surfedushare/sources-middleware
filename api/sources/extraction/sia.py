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
    def get_parties(cls, node):
        return [{"name": node["contactinformatie"]["naam"]}]


SiaProjectExtractProcessor.OBJECTIVE = {
    "external_id": "$.id",
    "title": "$.titel",
    "status": "$.status",
    "started_at": "$.startdatum",
    "ended_at": "$.einddatum",
    "coordinates": lambda node: [],
    "goal": "$.eindrapportage",
    "description": "$.samenvatting",
    "contact": lambda node: None,
    "owner": lambda node: None,
    "persons": lambda node: [],
    "keywords": lambda node: None,
    "parties": SiaProjectExtractProcessor.get_parties,
    "products": lambda node: [],
}
