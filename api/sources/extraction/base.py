from datagrowth.processors import ExtractProcessor


class SingleResponseExtraction(ExtractProcessor):

    CONTENT_TYPE = "application/json"
    response = None

    def __init__(self, config, response):
        super().__init__(config)
        self.response = response

    @property
    def data(self):
        return self.response.json()
