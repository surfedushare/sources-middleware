from django.urls import reverse


class PureAPIMixin(object):

    response = None
    config = None

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    def get_api_next_cursor_link(self, request, data):
        info = data["pageInformation"]
        next_offset = info['offset'] + info['size']
        if next_offset > self.get_api_count(data):
            return
        base_url = reverse("v1:entities", args=(self.config.entity, request.resolver_match.kwargs["source"]))
        return f"{request.build_absolute_uri(base_url)}?cursor=offset|{next_offset}|{info['size']}"

    def get_api_previous_cursor_link(self, request, data):
        info = data["pageInformation"]
        previous_offset = info['offset'] - info['size']
        if previous_offset < 0:
            return
        base_url = reverse("v1:entities", args=(self.config.entity, request.resolver_match.kwargs["source"]))
        return f"{request.build_absolute_uri(base_url)}?cursor=offset|{previous_offset}|{info['size']}"

    @classmethod
    def get_api_results_path(cls):
        return "$.items"
