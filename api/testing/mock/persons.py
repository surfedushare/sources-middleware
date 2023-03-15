import os
import json
from hashlib import md5
from copy import copy

from django.utils.text import slugify


PERSON_DEFAULTS = {
    "name": None,
    "external_id": None,
    "email": None,
    "orcid": None,
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


class PersonsMock(object):

    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        with open(os.path.join("testing", "mock", "fixtures", "persons.json"), encoding="utf-8") as fixtures_json:
            data = json.load(fixtures_json)
        return [
            self.build_person(person["value"], include_email=bool(ix % 2), include_orcid=not ix % 2)
            for ix, person in enumerate(data)
        ]

    def build_email(self, name):
        return f"{slugify(name)}@publinova-mock.nl"

    def build_person(self, name, include_email=True, include_orcid=False, external_id=None):
        if not external_id:
            hash = md5()
            hash.update(name.encode("utf-8"))
            external_id = hash.hexdigest()
        email = self.build_email(name) if include_email else None
        orcid = external_id if include_orcid else None
        person = copy(PERSON_DEFAULTS)
        person.update({
            "name": name,
            "external_id": external_id,
            "email": email,
            "orcid": orcid,
        })
        return person


class PartialPersonsMock(PersonsMock):

    def load_data(self):
        with open(os.path.join("testing", "mock", "fixtures", "persons.json"), encoding="utf-8") as fixtures_json:
            data = json.load(fixtures_json)
        return [
            self.build_person(person["value"], include_email=False, include_orcid=not ix % 2, external_id=person["id"])
            for ix, person in enumerate(data)
        ]


class UserMock(PersonsMock):
    def load_data(self):
        with open(os.path.join("testing", "mock", "fixtures", "persons.json"), encoding="utf-8") as fixtures_json:
            data = json.load(fixtures_json)
        return [
            self.build_person(person["value"], include_email=True, include_orcid=not ix % 2, external_id=person["id"])
            for ix, person in enumerate(data)
        ]
