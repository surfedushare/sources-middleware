from hashlib import md5
from copy import copy

from testing.constants import PROJECT_DEFAULTS


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
        project = copy(PROJECT_DEFAULTS)
        project.update({
            "title": title,
            "external_id": external_id
        })
        return project
