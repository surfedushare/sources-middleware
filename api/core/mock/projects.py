from hashlib import md5


class ProjectsMock(object):

    def __init__(self):
        self.data = [
            self.build_project(f"project {str(ix).rjust(3, '0')}")
            for ix in range(1, 201)
        ]

    def build_project(self, title):
        hash = md5()
        hash.update(title.encode("utf-8"))
        external_id = hash.hexdigest()
        return {
            "title": title,
            "external_id": external_id,
            "status": None,
            "started_at": None,
            "ended_at": None,
            "coordinates": [0, 0],
            "goal": None,
            "contact": None,
            "persons": [],
            "owner": None,
            "description": None,
            "parties": [],
            "keywords": [],
            "products": [],
            "projects": [],
            "photo_url": None
        }
