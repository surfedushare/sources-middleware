from datagrowth.processors import ExtractProcessor


class SingleResponseExtractProcessor(ExtractProcessor):

    CONTENT_TYPE = "application/json"
    response = None

    def __init__(self, config, response):
        super().__init__(config)
        self.response = response

    @property
    def data(self):
        return self.response.json()


class SinglePageAPIMixin(object):

    @classmethod
    def get_api_count(cls, data):
        return len(data)

    def get_api_next_cursor_link(self, data):
        return None

    def get_api_previous_cursor_link(self, data):
        return None

    @classmethod
    def get_api_results_path(cls):
        return "$"
