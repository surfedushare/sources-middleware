from requests import Session, Request, Response
from copy import copy
import json
from io import BytesIO

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as APIValidationError
from datagrowth.processors import Processor
from datagrowth.utils import reach

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
        elif self.auth["type"] == AuthenticationTypes.BEARER_TOKEN_HEADER:
            request.headers.update({
                "Authorization": f"Bearer {self.auth['token']}"
            })
        elif self.auth["type"] == AuthenticationTypes.OCP_APIM:
            request.headers.update({
                "Ocp-Apim-Subscription-Key": self.auth['token']
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


class SourceIdentifierListProxy(SourceProxy):

    def __init__(self, base, endpoints, auth=None, pagination=None):
        super().__init__(base, endpoints, auth=auth, pagination=pagination)
        assert base["identifier_list"], \
            "Expected base source configuration to contain an identifier_list key for SourceIdentifierListProxy"
        assert pagination["type"] == PaginationTypes.OFFSET, "Expected offset pagination for SourceIdentifierListProxy"

    def extract_identifiers(self, response, cursor):
        data = response.json()
        pagination_parameters = self.parse_pagination_parameters(cursor)
        start = pagination_parameters["offset"]
        end = pagination_parameters["offset"] + pagination_parameters["size"]
        return {
            "count": len(data),
            "pagination": pagination_parameters,
            "identifiers": [
                reach(self.base["identifier_list"]["identifier_path"], obj)
                for obj in data[start:end]
            ]
        }

    def build_detail_request(self, entity, identifier):
        url = f"{self.base['url']}{self.endpoints[entity]['url']}/{identifier}"
        request = Request(
            "GET", url,
            params=copy(self.base['parameters']),
            headers=copy(self.base['headers'])
        )
        if self.auth:
            request = self._apply_request_authentication(request)
        return request

    def fetch(self, entity, cursor=None):
        assert cursor, "Expected a cursor to be able to fetch using a SourceIdentifierListProxy"
        list_response = super().fetch(entity, cursor=None)
        data = self.extract_identifiers(list_response, cursor)
        session = Session()
        results = []
        for identifier in data.pop("identifiers"):
            request = self.build_detail_request(entity, identifier)
            prepared_request = request.prepare()  # NB: cookies or other state is not supported
            response = session.send(prepared_request)
            results.append(response.json())
        data["results"] = results
        io_response = Response()
        io_response.status_code = 200
        io_response.raw = BytesIO(json.dumps(data).encode("utf-8"))
        return io_response


class SourceMultipleResourcesProxy(SourceProxy):

    def __init__(self, base, endpoints, auth=None, pagination=None):
        super().__init__(base, endpoints, auth=auth, pagination=pagination)
        assert base["resources"], \
            "Expected base source configuration to contain a resources key for SourceMultipleResourcesProxy"
        assert pagination["type"] == PaginationTypes.OFFSET, \
            "Expected offset pagination for SourceMultipleResourcesProxy"

    def extract_resource_identifiers(self, response, cursor, resource_config):
        data = response.json()
        results = reach(resource_config["results_path"], data)
        if not results:
            return []
        pagination_parameters = self.parse_pagination_parameters(cursor)
        start = pagination_parameters["offset"]
        end = pagination_parameters["offset"] + pagination_parameters["size"]
        return [
            reach(resource_config["resource_id"], obj)
            for obj in results[start:end]
        ]

    def build_resource_request(self, resource_config, identifier):
        url = f"{self.base['url']}{resource_config['url']}/{identifier}"
        request = Request(
            "GET", url,
            params=copy(self.base['parameters']),
            headers=copy(self.base['headers'])
        )
        if self.auth:
            request = self._apply_request_authentication(request)
        return request

    def fetch(self, entity, cursor=None):
        assert cursor, "Expected a cursor to be able to fetch using a SourceIdentifierListProxy"
        # Fetch the list of main resources
        partial_response = super().fetch(entity, cursor=None)
        partial_data = partial_response.json()
        # For each subresource gather the data and write it onto the main resource
        session = Session()
        for resource_name, resource_config in self.base["resources"][entity].items():
            identifiers = self.extract_resource_identifiers(partial_response, cursor, resource_config)
            resource_data = {}
            for identifier in identifiers:
                request = self.build_resource_request(resource_config, identifier)
                prepared_request = request.prepare()  # NB: cookies or other state is not supported
                response = session.send(prepared_request)
                resource_data[identifier] = response.json()
            for result in reach(resource_config["results_path"], partial_data):
                identifier = reach(resource_config["resource_id"], result)
                result[resource_name] = resource_data[identifier]
        # Return as a readable response for the view method that uses this proxy class
        io_response = Response()
        io_response.status_code = 200
        io_response.raw = BytesIO(json.dumps(partial_data).encode("utf-8"))
        return io_response
