import os
import json
from hashlib import md5

from django.utils.text import slugify


class PersonsMock(object):

    def __init__(self):
        with open(os.path.join("core", "mock", "fixtures", "persons.json"), encoding="utf-8") as fixtures_json:
            data = json.load(fixtures_json)
        self.data = [
            self.build_person(person["value"], bool(ix % 2), not ix % 2)
            for ix, person in enumerate(data)
        ]

    def build_person(self, name, include_email=True, include_orcid=False):
        hash = md5()
        hash.update(name.encode("utf-8"))
        external_id = hash.hexdigest()
        email = f"{slugify(name)}@publinova-mock.nl" if include_email else None
        orcid = external_id if include_orcid else None
        return {
            "name": name,
            "external_id": external_id,
            "email": email,
            "orcid": orcid,
            "isni": None,
            "dai": None,
            "first_name": None,
            "last_name": None,
            "prefix": None,
            "initials": None,
            "title": None,
            "phone": None,
            "skills": [],
            "themes": [],
            "description": None,
            "parties": [],
            "photo_url": None,
            "is_employed": True
        }
