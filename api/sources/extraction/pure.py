class PureAPIMixin(object):

    response = None
    config = None

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    def get_api_next_cursor(self, data):
        info = data["pageInformation"]
        next_offset = info['offset'] + info['size']
        if next_offset > self.get_api_count(data):
            return
        return f"offset|{next_offset}|{info['size']}"

    def get_api_previous_cursor(self, data):
        info = data["pageInformation"]
        previous_offset = info['offset'] - info['size']
        if previous_offset < 0:
            return
        return f"offset|{previous_offset}|{info['size']}"

    @classmethod
    def get_api_results_path(cls):
        return "$.items"
