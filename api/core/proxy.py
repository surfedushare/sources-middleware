from requests import Session, Request
from copy import copy

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as APIValidationError
from datagrowth.processors import Processor

from core.constants import PaginationTypes, AuthenticationTypes


class SourceProxy(object):

    endpoints = {}
    auth = {}
    pagination = {}

    def __init__(self, base, endpoints, auth=None, pagination=None):
        self.base = base
        self.endpoints = endpoints
        self.auth = auth
        self.pagination = pagination

    def validate_cursor(self, cursor):
        if not self.pagination:
            return
        pagination_type = self.pagination["type"]
        if pagination_type == PaginationTypes.CURSOR:
            return cursor
        if cursor is None:
            return "{}|{}|{}".format(
                self.pagination["type"].value,
                *self.pagination["parameters"].values()
            )

        cursor_validator = RegexValidator(f"{pagination_type.value}\|\d+\|\d+")
        try:
            cursor_validator(cursor)
        except ValidationError:
            raise APIValidationError(detail=f"Invalid cursor for pagination {pagination_type.value}")
        return cursor

    def is_implemented(self, entity):
        return bool(self.endpoints.get(entity, None))

    def _apply_request_authentication(self, request):
        if self.auth["type"] == AuthenticationTypes.API_KEY_HEADER:
            request.headers.update({
                "api-key": self.auth["token"]
            })
        return request

    def parse_pagination_parameters(self, cursor):
        if not self.pagination:
            return {}
        if self.pagination["type"] in [PaginationTypes.PAGE, PaginationTypes.OFFSET]:
            prefix, first, second = cursor.split("|")
            return {
                key: int(value)
                for key, value in zip(self.pagination["parameters"].keys(), (first, second,))
            }
        elif self.pagination["type"] == PaginationTypes.CURSOR:
            cursor_key = next(self.pagination["parameter"].keys())
            return {
                cursor_key: cursor
            }

    def build_request(self, entity, cursor=None):
        url = f"{self.base['url']}{self.endpoints[entity]['url']}"
        request = Request(
            "GET", url,
            params=copy(self.base['parameters']),
            headers=copy(self.base['headers'])
        )
        if cursor:
            request.params.update(self.parse_pagination_parameters(cursor))
        if self.auth:
            request = self._apply_request_authentication(request)
        return request

    def fetch(self, entity, cursor=None):
        request = self.build_request(entity, cursor)
        prepared_request = request.prepare()  # NB: cookies or other state is not supported
        session = Session()
        return session.send(prepared_request)

    def build_extractor(self, entity, response):
        Extractor = Processor.get_processor_class(self.endpoints[entity]["extractor"])
        objective = copy(Extractor.OBJECTIVE)
        objective["@"] = Extractor.get_api_results_path()
        config = {
            "entity": entity,
            "objective": objective
        }
        return Extractor(config, response)
